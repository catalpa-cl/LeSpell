"""Analysis utilities for spelling errors and corrections."""

from typing import List, Tuple

from lespell.core import SpellingItem


def calculate_levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings.

    Args:
        s1: First string
        s2: Second string

    Returns:
        Levenshtein distance (number of edits)
    """
    if len(s1) < len(s2):
        return calculate_levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row: List[int] = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def calculate_normalized_levenshtein(s1: str, s2: str) -> float:
    """Calculate normalized Levenshtein distance (0 to 1).

    Args:
        s1: First string
        s2: Second string

    Returns:
        Normalized distance (0 = identical, 1 = completely different)
    """
    distance = calculate_levenshtein_distance(s1, s2)
    max_length = max(len(s1), len(s2))
    if max_length == 0:
        return 0.0
    return distance / max_length


def analyze_error_distances(items: List[SpellingItem]) -> dict:
    """Analyze average Levenshtein distances for errors in items.

    Args:
        items: List of SpellingItem objects

    Returns:
        Dictionary with statistics (mean, min, max, count)
    """
    distances = []

    for item in items:
        text = item.text
        for span, correction in item.corrections.items():
            start, end = map(int, span.split("-"))
            misspelled = text[start:end]
            distance = calculate_levenshtein_distance(misspelled, correction)
            distances.append(distance)

    if not distances:
        return {"count": 0, "mean": 0.0, "min": 0, "max": 0}

    return {
        "count": len(distances),
        "mean": sum(distances) / len(distances),
        "min": min(distances),
        "max": max(distances),
    }


def analyze_error_types(items: List[SpellingItem]) -> dict:
    """Analyze distribution of error types.

    Args:
        items: List of SpellingItem objects

    Returns:
        Dictionary mapping error types to counts
    """
    error_types: dict = {}

    for item in items:
        for _span, error_type in item.correction_error_types.items():
            error_types[error_type] = error_types.get(error_type, 0) + 1

    return error_types


def get_corpus_statistics(items: List[SpellingItem]) -> dict:
    """Get overall statistics for a corpus.

    Args:
        items: List of SpellingItem objects

    Returns:
        Dictionary with corpus statistics
    """
    total_texts = len(items)
    total_spelling_errors = sum(item.num_spelling_errors for item in items)
    total_grammar_errors = sum(item.num_grammar_errors for item in items)
    total_tokens = sum(len(item.text.split()) for item in items)
    total_chars = sum(len(item.text) for item in items)

    avg_text_length = total_chars / total_texts if total_texts > 0 else 0
    avg_errors_per_text = total_spelling_errors / total_texts if total_texts > 0 else 0

    return {
        "total_texts": total_texts,
        "total_spelling_errors": total_spelling_errors,
        "total_grammar_errors": total_grammar_errors,
        "total_tokens": total_tokens,
        "total_characters": total_chars,
        "avg_text_length": avg_text_length,
        "avg_errors_per_text": avg_errors_per_text,
        "error_density": total_spelling_errors / total_tokens if total_tokens > 0 else 0,
    }


def find_similar_errors(
    items: List[SpellingItem], max_distance: int = 1
) -> List[Tuple[str, str, int]]:
    """Find similar misspellings (within max_distance).

    Args:
        items: List of SpellingItem objects
        max_distance: Maximum Levenshtein distance to consider as similar

    Returns:
        List of (misspelled, correction, distance) tuples for similar errors
    """
    similar_errors = []
    misspellings = {}

    # Collect all misspellings
    for item in items:
        text = item.text
        for span, correction in item.corrections.items():
            start, end = map(int, span.split("-"))
            misspelled = text[start:end]

            if misspelled not in misspellings:
                misspellings[misspelled] = correction

    # Find similar ones
    misspelled_list = list(misspellings.keys())
    for i, misspelled1 in enumerate(misspelled_list):
        for misspelled2 in misspelled_list[i + 1 :]:
            distance = calculate_levenshtein_distance(misspelled1, misspelled2)
            if distance <= max_distance:
                similar_errors.append((misspelled1, misspellings[misspelled1], distance))

    return similar_errors
