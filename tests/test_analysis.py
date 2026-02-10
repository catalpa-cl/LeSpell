"""Tests for analysis utilities."""

import pytest

from lespell.analysis import (
    analyze_error_distances,
    analyze_error_types,
    calculate_levenshtein_distance,
    calculate_normalized_levenshtein,
    find_similar_errors,
    get_corpus_statistics,
)
from lespell.core import SpellingItem


class TestLevenshteinDistance:
    """Test Levenshtein distance calculations."""

    def test_identical_strings(self):
        """Identical strings should have distance 0."""
        assert calculate_levenshtein_distance("hello", "hello") == 0

    def test_empty_strings(self):
        """Empty strings should have distance 0."""
        assert calculate_levenshtein_distance("", "") == 0

    def test_one_empty(self):
        """Distance to empty string is string length."""
        assert calculate_levenshtein_distance("hello", "") == 5
        assert calculate_levenshtein_distance("", "hello") == 5

    def test_substitution(self):
        """Single character substitution."""
        assert calculate_levenshtein_distance("cat", "bat") == 1
        assert calculate_levenshtein_distance("sit", "set") == 1

    def test_insertion(self):
        """Single character insertion."""
        assert calculate_levenshtein_distance("cat", "cats") == 1
        assert calculate_levenshtein_distance("hat", "chat") == 1

    def test_deletion(self):
        """Single character deletion."""
        assert calculate_levenshtein_distance("cats", "cat") == 1
        assert calculate_levenshtein_distance("chat", "hat") == 1

    def test_multiple_operations(self):
        """Multiple operations."""
        assert calculate_levenshtein_distance("kitten", "sitting") == 3

    def test_normalized_distance(self):
        """Normalized distance should be between 0 and 1."""
        dist = calculate_normalized_levenshtein("hello", "hallo")
        assert 0 <= dist <= 1
        dist = calculate_normalized_levenshtein("identical", "identical")
        assert dist == 0.0


class TestAnalyzeErrors:
    """Test error analysis functions."""

    @pytest.fixture
    def sample_items(self):
        """Create sample spelling items for testing."""
        return [
            SpellingItem(
                corpus_name="test",
                text_id="1",
                text="This is a tst with a error.",
                corrections={"10-13": "test"},
                correction_error_types={"10-13": "spelling"},
                grammar_corrections={"20-21": "an"},
            ),
            SpellingItem(
                corpus_name="test",
                text_id="2",
                text="Anohter misspeling here.",
                corrections={"0-7": "Another", "8-19": "misspelling"},
                correction_error_types={"0-7": "spelling", "8-19": "spelling"},
            ),
        ]

    def test_analyze_error_distances(self, sample_items):
        """Test error distance analysis."""
        stats = analyze_error_distances(sample_items)

        assert stats["count"] > 0
        assert "mean" in stats
        assert "min" in stats
        assert "max" in stats

    def test_analyze_error_types(self, sample_items):
        """Test error type analysis."""
        types = analyze_error_types(sample_items)

        assert "spelling" in types
        assert types["spelling"] > 0

    def test_corpus_statistics(self, sample_items):
        """Test corpus statistics."""
        stats = get_corpus_statistics(sample_items)

        assert stats["total_texts"] == 2
        assert stats["total_spelling_errors"] == 3
        assert stats["total_grammar_errors"] == 1
        assert stats["avg_errors_per_text"] == 1.5  # (3 spelling + 1 grammar) / 2 texts

    def test_find_similar_errors(self, sample_items):
        """Test finding similar errors."""
        similar = find_similar_errors(sample_items, max_distance=2)

        # Should find some similar misspellings
        assert isinstance(similar, list)
