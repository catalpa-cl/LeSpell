"""Candidate ranking and reranking strategies."""

import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

try:
    import torch
    from transformers import AutoTokenizer, pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False


class Ranker(ABC):
    """Abstract base class for ranking strategies."""

    @abstractmethod
    def rank(
        self,
        candidates: List[Tuple[str, float]],
        context: Optional[str] = None,
        misspelled: Optional[str] = None,
    ) -> List[Tuple[str, float]]:
        """Rank candidates.

        Args:
            candidates: List of (word, cost) tuples
            context: Optional surrounding context
            misspelled: Original misspelled word

        Returns:
            Re-ranked list of (word, cost) tuples
        """
        pass


class CostBasedRanker(Ranker):
    """Simple ranker that uses cost only."""

    def rank(
        self,
        candidates: List[Tuple[str, float]],
        context: Optional[str] = None,
        misspelled: Optional[str] = None,
    ) -> List[Tuple[str, float]]:
        """Return candidates sorted by cost."""
        return sorted(candidates, key=lambda x: x[1])


class MaskedLanguageModelRanker(Ranker):
    """Rank candidates using masked language model.

    TODO: Integrate with HuggingFace for masked language model scoring.
    """

    def __init__(
        self,
        model_name: str = "distilbert-base-uncased",
        device: int = -1,
    ):
        """Initialize masked language model ranker.

        Args:
            model_name: HuggingFace model name (e.g., "bert-base-uncased")
            device: Device to use for inference. -1 for CPU, 0+ for CUDA device.
                   Defaults to -1 (CPU). If device >= 0 and CUDA is available, uses GPU.
        """
        if not HAS_TRANSFORMERS:
            raise ImportError(
                "transformers library not found. Install with: pip install transformers torch"
            )
        self.model_name = model_name
        self.device = device if device >= 0 and torch.cuda.is_available() else -1
        self.pipe = None
        self.tokenizer = None
        self.__mask_token = None


    def _initialize_huggingface_model(self) -> None:
        """Initialize HuggingFace transformer model for contextual scoring.

        Loads the tokenizer and fill-mask pipeline from the specified model.
        Model is loaded lazily on first use for performance.
        """
        if self.pipe is not None:
            # Already initialized
            return

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.pipe = pipeline(
                "fill-mask",
                model=self.model_name,
                device=self.device,
            )
            # Get mask token from tokenizer
            if not hasattr(self.tokenizer, "mask_token") or self.tokenizer.mask_token is None:
                raise ValueError(
                    f"Model '{self.model_name}' does not support masked language modeling."
                )
            self.__mask_token = self.tokenizer.mask_token
        except Exception as e:
            raise RuntimeError(
                f"Failed to load model '{self.model_name}': {e}. "
                f"Make sure the model name is correct and 'transformers' is installed."
            )

    def _score_with_huggingface(
        self, candidates: List[str], context: str, misspelled: Optional[str]
    ) -> Dict[str, float]:
        """Score candidates using HuggingFace masked language model.

        Replaces the misspelled word with [MASK] in context and scores each
        candidate using the masked language model.

        Args:
            candidates: List of candidate correction words
            context: Context string containing the misspelled word
            misspelled: The original misspelled word (to find and mask)

        Returns:
            Dictionary mapping candidate words to their probability scores (0-1)
        """
        if misspelled is None:
            # Without knowing what to mask, we can't score
            return {}

        # Ensure model is initialized
        self._initialize_huggingface_model()

        # Find and replace misspelled word with mask token
        # Use case-insensitive matching but preserve context structure
        masked_context = context.replace(misspelled, self.__mask_token)

        # If replacement didn't work (e.g., case mismatch), try case-insensitive
        if self.__mask_token not in masked_context:
            pattern = re.compile(re.escape(misspelled), re.IGNORECASE)
            masked_context = pattern.sub(self.__mask_token, context, count=1)

        # Score each candidate using the fill-mask pipeline
        scores = {}
        try:
            results = self.pipe(
                masked_context,
                targets=candidates,
                top_k=len(candidates),
            )
        except Exception as e:
            # If something goes wrong with scoring, return empty dict
            # (will trigger fallback to cost-based ranking)
            return {}

        # Extract scores from results
        # Results are sorted by score (highest first)
        if isinstance(results, list):
            for result in results:
                token_str = result.get("token_str", "").strip()
                score = result.get("score", 0.0)
                # Match against candidates (may include subword tokens)
                for candidate in candidates:
                    if candidate.lower() in token_str.lower() or token_str.lower() in candidate.lower():
                        if candidate not in scores:
                            scores[candidate] = score
                        break

        return scores

    def rank(
        self,
        candidates: List[Tuple[str, float]],
        context: Optional[str] = None,
        misspelled: Optional[str] = None,
    ) -> List[Tuple[str, float]]:
        """Rank candidates using language model.

        If context is provided, uses masked language model to score candidates
        contextually. Otherwise falls back to cost-based ranking.

        Args:
            candidates: List of (word, cost) tuples
            context: Optional surrounding context string
            misspelled: Original misspelled word (needed for masking)

        Returns:
            Re-ranked list of (word, cost) tuples, sorted by LM score (best first)
        """
        if not context or misspelled is None:
            # Without context or knowing what to mask, use cost-based ranking
            return sorted(candidates, key=lambda x: x[1])

        # Extract candidate words
        candidate_words = [word for word, _ in candidates]

        # Score with language model
        lm_scores = self._score_with_huggingface(
            candidate_words, context, misspelled
        )

        # If we got no scores, fall back to cost-based ranking
        if not lm_scores:
            return sorted(candidates, key=lambda x: x[1])

        # Convert LM probabilities to costs and re-rank
        # Higher LM probability = lower cost (better ranking)
        reranked = []
        for word, _ in candidates:
            if word in lm_scores:
                # Convert probability to cost: cost = 1 - probability
                # This inverts the score so higher probability → lower cost
                lm_cost = 1.0 - lm_scores[word]
                reranked.append((word, lm_cost))
            else:
                # If no LM score, use a penalty (higher than any valid score)
                reranked.append((word, 1.0))

        # Sort by cost (LM-based), then by original cost as tiebreaker
        reranked.sort(key=lambda x: x[1])
        return reranked


# TODO are we sure we want the ensemble to work like this? Maybe we should just average the scores instead of using rank-based scoring?
class EnsembleRanker(Ranker):
    """Combine multiple rankers (weighted ensemble)."""

    def __init__(self, rankers: List[Tuple[Ranker, float]]):
        """Initialize with list of (ranker, weight) tuples."""
        self.rankers = rankers
        total_weight = sum(w for _, w in rankers)
        if total_weight != 1.0:
            # Normalize weights
            self.rankers = [(r, w / total_weight) for r, w in rankers]

    def rank(
        self,
        candidates: List[Tuple[str, float]],
        context: Optional[str] = None,
        misspelled: Optional[str] = None,
    ) -> List[Tuple[str, float]]:
        """Rank using ensemble of rankers."""

        # Score with each ranker
        word_scores: Dict[str, float] = {}

        for ranker, weight in self.rankers:
            ranked = ranker.rank(candidates, context, misspelled)
            for rank, (word, cost) in enumerate(ranked):
                # Inverse of rank (lower rank = higher score)
                normalized_cost = 1.0 - cost  # assuming cost is 0-1
                score = weight * (1.0 / (rank + 1)) * normalized_cost
                word_scores[word] = word_scores.get(word, 0) + score

        # Sort by ensemble score
        ensemble_ranked = sorted(word_scores.items(), key=lambda x: -x[1])

        # Return with original costs
        result = []
        for word, _ in ensemble_ranked:
            original_cost = next((c for w, c in candidates if w == word), 1.0)
            result.append((word, original_cost))

        return result
