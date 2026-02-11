"""Analysis utilities for spelling errors and corrections."""

from lespell.analysis.evaluation import CorrectionEvaluator, DetectionEvaluator
from lespell.analysis.utils import (
    analyze_error_distances,
    analyze_error_types,
    calculate_levenshtein_distance,
    calculate_normalized_levenshtein,
    find_similar_errors,
    get_corpus_statistics,
)

__all__ = [
    "calculate_levenshtein_distance",
    "calculate_normalized_levenshtein",
    "analyze_error_distances",
    "analyze_error_types",
    "get_corpus_statistics",
    "find_similar_errors",
    "CorrectionEvaluator",
    "DetectionEvaluator",
]
