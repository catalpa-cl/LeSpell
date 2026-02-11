"""Main spelling checker orchestrator."""

from typing import List, Optional, Dict, Tuple

from lespell.spellchecker.annotations import Text, Annotation
from lespell.spellchecker.candidates import CandidateGenerator
from lespell.spellchecker.detection import ErrorDetector
from lespell.spellchecker.ranking import Ranker, CostBasedRanker
from lespell.io import SpellingItem


class SpellingChecker:
    """Spelling checker orchestrating detection, correction, and ranking phases.

    The checker comprises three distinct phases:
    1. Error Detection: Identifies spelling errors in text
    2. Correction Generation: Generates candidate corrections for each error
    3. Ranking: Ranks candidates by quality
    """

    def __init__(
        self,
        detector: ErrorDetector,
        candidate_generators: List[CandidateGenerator],
        ranker: Optional[Ranker] = None,
    ):
        """Initialize spell checker.

        Args:
            detector: ErrorDetector instance for phase 1
            candidate_generators: List of candidate generation strategies (phase 2)
            ranker: Ranking strategy for phase 3 (default: CostBasedRanker)
        """
        self.detector = detector
        self.candidate_generators = candidate_generators
        self.ranker = ranker or CostBasedRanker()

    def check_text(
        self, text_content: str, context_window: int = 5
    ) -> Dict:
        """Check text for spelling errors using three-phase workflow.

        Args:
            text_content: Text to check
            context_window: Context window size for each error

        Returns:
            Dictionary with errors and suggestions
        """
        text = Text(content=text_content)

        # Phase 1: Error Detection
        text, errors = self.detector.detect(text)

        results = []

        # Phases 2 & 3: Correction Generation and Ranking
        for error in errors:
            word = error.word

            # Get context
            context_start = max(0, error.start - context_window * 5)
            context_end = min(len(text_content), error.end + context_window * 5)
            context = text_content[context_start:context_end]

            # Generate candidates from all generators
            all_candidates = []
            for generator in self.candidate_generators:
                try:
                    generated = generator.generate(word, context)
                    for cand_word, cost in generated:
                        all_candidates.append(
                            (cand_word, cost, generator.__class__.__name__)
                        )
                except (NotImplementedError, Exception):
                    # Skip generators that aren't implemented or fail
                    pass

            # Deduplicate candidates (keep lowest cost)
            seen = {}
            for cand_word, cost, method in all_candidates:
                if cand_word not in seen or cost < seen[cand_word][0]:
                    seen[cand_word] = (cost, method)

            # Convert back to list, sort, and keep top 10
            candidates = [(w, c, m) for w, (c, m) in seen.items()]
            candidates.sort(key=lambda x: x[1])
            candidates = candidates[:10]

            # Rank candidates
            ranked = self.ranker.rank(
                [(w, c) for w, c, _ in candidates],
                context=context,
                misspelled=word,
            )

            results.append(
                {
                    "start": error.start,
                    "end": error.end,
                    "word": word,
                    "context": context,
                    "suggestions": [w for w, _ in ranked[:5]],
                    "scores": [c for _, c in ranked[:5]],
                    "methods": [m for _, _, m in candidates[:5]],
                }
            )

        return {
            "text": text_content,
            "errors": results,
            "error_count": len(errors),
        }

    def correct_text(self, text_content: str, auto_correct: bool = False) -> str:
        """Correct text using top-1 suggestions.

        Args:
            text_content: Text to correct
            auto_correct: If True, apply corrections; otherwise just return suggestions

        Returns:
            Corrected text (or original if auto_correct=False)
        """
        check_results = self.check_text(text_content)

        if not auto_correct:
            return text_content

        # Apply corrections starting from end (to maintain positions)
        corrected = list(text_content)

        for error in reversed(check_results["errors"]):
            if error["suggestions"]:
                correction = error["suggestions"][0]
                corrected[error["start"] : error["end"]] = list(correction)

        return "".join(corrected)

    def check_spelling_items(self, items: List[SpellingItem]) -> List[Dict]:
        """Check multiple SpellingItem objects.

        Args:
            items: List of SpellingItem objects

        Returns:
            List of check results with error information
        """
        results = []

        for item in items:
            check_result = self.check_text(item.text)
            check_result["corpus_name"] = item.corpus_name
            check_result["text_id"] = item.text_id
            check_result["gold_corrections"] = item.corrections
            results.append(check_result)

        return results
