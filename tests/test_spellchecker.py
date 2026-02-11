"""Tests for the main SpellingChecker class."""

import unittest

from lespell.spellchecker import (
    SpellingChecker,
    LevenshteinCandidateGenerator,
    CostBasedRanker,
    DictionaryErrorDetector,
)
from lespell.io import SpellingItem


def create_test_dictionary_set():
    """Create a simple test dictionary as set."""
    return {
        "this", "is", "a", "test", "of", "the", "spelling", "checker",
        "quick", "brown", "fox", "jumps", "over", "lazy", "dog",
        "received", "package", "yesterday", "excellent", "communication", "skills",
    }


class TestSpellingChecker(unittest.TestCase):
    """Test SpellingChecker orchestrator."""

    def setUp(self):
        """Set up test fixtures."""
        dictionary = create_test_dictionary_set()
        self.generator = LevenshteinCandidateGenerator(
            language="en",
            dictionary=dictionary,
            substitution_weight=1.0,
            deletion_weight=1.0,
            insertion_weight=1.0,
            transposition_weight=1.0,
            max_candidates=10,
        )
        self.ranker = CostBasedRanker()
        
        # Create detector with the dictionary
        self.detector = DictionaryErrorDetector(dictionary=dictionary)
        
        self.checker = SpellingChecker(
            detector=self.detector,
            candidate_generators=[self.generator],
            ranker=self.ranker,
        )

    def test_checker_initialization(self):
        """Test SpellingChecker initialization."""
        self.assertIsNotNone(self.checker.detector)
        self.assertIsNotNone(self.checker.ensemble)
        self.assertIsNotNone(self.checker.ranker)

    def test_check_text_basic(self):
        """Test basic text checking."""
        text = "This is a tset of the speling checker."
        result = self.checker.check_text(text)

        self.assertEqual(result["text"], text)
        self.assertIn("error_count", result)
        self.assertIn("errors", result)
        self.assertIsInstance(result["errors"], list)

    def test_correct_text_no_auto_correct(self):
        """Test text correction without auto-correct."""
        text = "This is a tset."
        corrected = self.checker.correct_text(text, auto_correct=False)

        # Should return original text without auto-correct
        self.assertEqual(corrected, text)

    def test_check_spelling_items(self):
        """Test checking multiple SpellingItem objects."""
        items = [
            SpellingItem(
                corpus_name="test",
                text_id="1",
                text="This is a tset.",
                corrections={"10-14": "test"},
            ),
            SpellingItem(
                corpus_name="test",
                text_id="2",
                text="Another mispelled word.",
                corrections={"8-17": "misspelled"},
            ),
        ]

        results = self.checker.check_spelling_items(items)

        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIn("corpus_name", result)
            self.assertIn("text_id", result)
            self.assertIn("gold_corrections", result)
            self.assertIn("errors", result)

    def test_checker_with_single_generator(self):
        """Test SpellingChecker with minimal setup."""
        dictionary = create_test_dictionary_set()
        generator = LevenshteinCandidateGenerator(
            language="en",
            dictionary=dictionary,
            substitution_weight=1.0,
            max_candidates=5,
        )
        
        detector = DictionaryErrorDetector.__new__(DictionaryErrorDetector)
        detector.dictionary = dictionary
        detector.dictionary_path = None
        
        checker = SpellingChecker(
            detector=detector,
            candidate_generators=[generator],
        )
        self.assertIsNotNone(checker)
        # Should use default CostBasedRanker
        self.assertIsNotNone(checker.ranker)
    def test_check_text_with_context(self):
        """Test that error results include context."""
        text = "The qwick brown fox jumps over the lazi dog."
        result = self.checker.check_text(text, context_window=3)

        self.assertIn("errors", result)
        if result["errors"]:
            error = result["errors"][0]
            self.assertIn("word", error)
            self.assertIn("context", error)
            self.assertIn("suggestions", error)
            self.assertIn("scores", error)

    def test_levenshtein_requires_dictionary(self):
        """Test that LevenshteinCandidateGenerator requires a dictionary."""
        with self.assertRaises(ValueError) as context:
            LevenshteinCandidateGenerator(language="en")
        
        self.assertIn("REQUIRES a dictionary", str(context.exception))

    def test_levenshtein_accepts_dict_parameter(self):
        """Test that LevenshteinCandidateGenerator accepts dictionary parameter."""
        dictionary = {"test", "dict"}
        generator = LevenshteinCandidateGenerator(
            language="en",
            dictionary=dictionary
        )
        self.assertEqual(generator.dictionary, dictionary)


if __name__ == "__main__":
    unittest.main()
