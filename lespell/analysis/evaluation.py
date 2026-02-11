"""Evaluation metrics for spelling correction."""

from typing import List, Dict, Set, Tuple, Optional
import json


class CorrectionEvaluator:
    """Evaluate spelling correction results."""

    def __init__(self):
        self.true_positives = 0
        self.false_positives = 0
        self.true_negatives = 0
        self.false_negatives = 0
        self.results = []

    def evaluate_correction(
        self, text: str, predicted_correction: str, gold_correction: str
    ) -> bool:
        """Evaluate single correction.

        Args:
            text: Original text with error
            predicted_correction: Predicted correction
            gold_correction: Gold standard correction

        Returns:
            True if prediction matches gold standard
        """
        is_correct = predicted_correction.lower() == gold_correction.lower()

        if is_correct:
            self.true_positives += 1
        else:
            self.false_positives += 1

        self.results.append(
            {
                "text": text,
                "predicted": predicted_correction,
                "gold": gold_correction,
                "correct": is_correct,
            }
        )

        return is_correct

    def evaluate_recall_at_k(
        self, candidates: List[str], gold_correction: str, k: int = 5
    ) -> bool:
        """Check if gold correction is in top-k candidates.

        Args:
            candidates: Ranked list of candidates
            gold_correction: Gold standard correction
            k: Number of top candidates to check

        Returns:
            True if gold correction in top-k
        """
        for i, candidate in enumerate(candidates[:k]):
            if candidate.lower() == gold_correction.lower():
                return True
        return False

    def get_metrics(self) -> Dict[str, float]:
        """Get evaluation metrics."""
        total = max(self.true_positives + self.false_positives, 1)
        accuracy = self.true_positives / total

        return {
            "accuracy": accuracy,
            "true_positives": self.true_positives,
            "false_positives": self.false_positives,
            "total_corrections": total,
        }

    def save_results(self, path: str) -> None:
        """Save evaluation results to file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)


class DetectionEvaluator:
    """Evaluate error detection performance."""

    def __init__(self):
        self.true_positives = 0  # Correctly identified errors
        self.false_positives = 0  # Incorrectly identified as errors
        self.true_negatives = 0  # Correctly identified as correct
        self.false_negatives = 0  # Missed errors
        self.results = []

    def evaluate(
        self,
        predicted_errors: Set[Tuple[int, int]],
        gold_errors: Set[Tuple[int, int]],
    ) -> None:
        """Evaluate error detection.

        Args:
            predicted_errors: Set of (start, end) error spans
            gold_errors: Gold standard error spans
        """
        tp = len(predicted_errors & gold_errors)
        fp = len(predicted_errors - gold_errors)
        fn = len(gold_errors - predicted_errors)

        self.true_positives += tp
        self.false_positives += fp
        self.false_negatives += fn

    def get_metrics(self) -> Dict[str, float]:
        """Get detection metrics."""
        tp = self.true_positives
        fp = self.false_positives
        fn = self.false_negatives

        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        f1 = 2 * (precision * recall) / max(precision + recall, 0.001)

        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
        }
