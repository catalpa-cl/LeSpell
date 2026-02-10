"""Main spelling checker orchestrator."""

from typing import List, Optional, Dict, Tuple

from lespell.spellchecker.annotations import Text, Annotation
from lespell.spellchecker.candidates import (
    CandidateEnsemble,
    CandidateGenerator,
)
from lespell.spellchecker.preprocessing import SimplePreprocessor
from lespell.spellchecker.ranking import Ranker, CostBasedRanker
from lespell.core import SpellingItem


class SpellingChecker:
    """Sophisticated spelling checker with multiple correction strategies."""

    def __init__(
        self,
        candidate_generators: List[CandidateGenerator],
        ranker: Optional[Ranker] = None,
        preprocessor: Optional[SimplePreprocessor] = None,
    ):
        """Initialize spell checker.

        Args:
            candidate_generators: List of candidate generation strategies
            ranker: Ranking strategy (default: CostBasedRanker)
            preprocessor: Preprocessing pipeline (optional)
        """
        self.ensemble = CandidateEnsemble(candidate_generators)
        self.ranker = ranker or CostBasedRanker()
        self.preprocessor = preprocessor

    def check_text(
        self, text_content: str, context_window: int = 5
    ) -> Dict:
        """Check text for spelling errors.

        Args:
            text_content: Text to check
            context_window: Context window size for each error

        Returns:
            Dictionary with errors and suggestions
        """
        text = Text(content=text_content)

        # Preprocess if preprocessor available
        if self.preprocessor:
            text = self.preprocessor.preprocess(text)

        errors = text.get_annotations_by_type("spelling_error")
        results = []

        for error in errors:
            word = text.get_span_text(error.start, error.end)

            # Get context
            context_start = max(0, error.start - context_window * 5)
            context_end = min(len(text_content), error.end + context_window * 5)
            context = text_content[context_start:context_end]

            # Generate candidates
            candidates = self.ensemble.generate(word, context, top_k=10)

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
