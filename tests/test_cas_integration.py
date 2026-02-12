"""Tests for CAS integration with dkpro-cassis."""

import unittest

from cassis import Cas

from lespell.spellchecker import (
    DictionaryErrorDetector,
    LevenshteinCandidateGenerator,
    SpellingChecker,
    add_spelling_error,
    cas_to_text,
    create_cas,
    get_spelling_errors,
    get_tokens_from_cas,
    has_tokens,
    text_to_cas,
    tokenize_cas,
)
from lespell.spellchecker.annotations import Annotation, Text


class TestCASUtilities(unittest.TestCase):
    """Test CAS utility functions."""

    def test_create_cas(self):
        """Test creating a CAS."""
        text = "This is a test."
        cas = create_cas(text)

        self.assertIsInstance(cas, Cas)
        self.assertEqual(cas.sofa_string, text)

    def test_tokenize_cas(self):
        """Test tokenizing a CAS."""
        cas = create_cas("This is a test")
        tokenize_cas(cas)

        self.assertTrue(has_tokens(cas))
        tokens = get_tokens_from_cas(cas)
        self.assertEqual(len(tokens), 4)
        self.assertEqual(tokens[0], (0, 4, "This"))
        self.assertEqual(tokens[1], (5, 7, "is"))

    def test_has_tokens(self):
        """Test checking if CAS has tokens."""
        cas = create_cas("Test")

        # No tokens initially
        self.assertFalse(has_tokens(cas))

        # Add tokens
        tokenize_cas(cas)
        self.assertTrue(has_tokens(cas))

    def test_add_spelling_error(self):
        """Test adding spelling error to CAS."""
        cas = create_cas("This is a tset")
        add_spelling_error(cas, 10, 14)

        errors = get_spelling_errors(cas)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0], (10, 14, "tset"))

    def test_get_spelling_errors(self):
        """Test getting spelling errors from CAS."""
        cas = create_cas("This is a tset")
        add_spelling_error(cas, 10, 14)

        errors = get_spelling_errors(cas)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][2], "tset")

    def test_cas_to_text(self):
        """Test converting CAS to Text object."""
        cas = create_cas("This is a test")
        tokenize_cas(cas)

        text = cas_to_text(cas)

        self.assertIsInstance(text, Text)
        self.assertEqual(text.content, "This is a test")
        # Should have token annotations
        tokens = text.get_annotations_by_type("token")
        self.assertGreater(len(tokens), 0)

    def test_text_to_cas(self):
        """Test converting Text object to CAS."""
        text = Text(content="This is a test")
        text.add_annotation(Annotation(type="token", start=0, end=4))
        text.add_annotation(Annotation(type="token", start=5, end=7))

        cas = text_to_cas(text)

        self.assertIsInstance(cas, Cas)
        self.assertEqual(cas.sofa_string, "This is a test")
        # Should have token annotations
        tokens = list(
            cas.select("de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token")
        )
        self.assertEqual(len(tokens), 2)


class TestCASDetection(unittest.TestCase):
    """Test error detection with CAS."""

    def setUp(self):
        """Set up test fixtures."""
        self.dictionary = {"this", "is", "a", "test", "of", "the", "spelling"}
        self.detector = DictionaryErrorDetector(dictionary=self.dictionary)

    def test_detect_cas_basic(self):
        """Test basic error detection with CAS."""
        cas = create_cas("This is a tset")
        cas, errors = self.detector.detect_cas(cas)

        # Should find 1 error
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].word, "tset")
        self.assertEqual(errors[0].start, 10)
        self.assertEqual(errors[0].end, 14)

    def test_detect_cas_tokenizes_if_needed(self):
        """Test that detect_cas tokenizes if no tokens exist."""
        cas = create_cas("This is a tset")
        self.assertFalse(has_tokens(cas))

        cas, errors = self.detector.detect_cas(cas)

        # Should have tokenized
        self.assertTrue(has_tokens(cas))
        self.assertEqual(len(errors), 1)

    def test_detect_cas_uses_existing_tokens(self):
        """Test that detect_cas uses existing tokens."""
        cas = create_cas("This is a tset")
        tokenize_cas(cas)
        token_count = len(get_tokens_from_cas(cas))

        cas, errors = self.detector.detect_cas(cas)

        # Should use existing tokens (count should be same)
        self.assertEqual(len(get_tokens_from_cas(cas)), token_count)
        self.assertEqual(len(errors), 1)

    def test_detect_cas_adds_spelling_anomalies(self):
        """Test that detect_cas adds SpellingAnomaly annotations."""
        cas = create_cas("This is a tset")
        cas, errors = self.detector.detect_cas(cas)

        # Check CAS has SpellingAnomaly annotations
        anomalies = list(
            cas.select("de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.SpellingAnomaly")
        )
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0].begin, 10)
        self.assertEqual(anomalies[0].end, 14)


class TestCASSpellingChecker(unittest.TestCase):
    """Test SpellingChecker with CAS."""

    def setUp(self):
        """Set up test fixtures."""
        self.dictionary = {
            "this",
            "is",
            "a",
            "test",
            "of",
            "the",
            "spelling",
            "checker",
        }
        detector = DictionaryErrorDetector(dictionary=self.dictionary)
        generator = LevenshteinCandidateGenerator(
            language="en",
            dictionary=self.dictionary,
            max_candidates=10,
        )

        self.checker = SpellingChecker(
            detector=detector,
            candidate_generators=[generator],
        )

    def test_check_cas_basic(self):
        """Test basic spell checking with CAS."""
        cas = create_cas("This is a tset")
        cas, result = self.checker.check_cas(cas)

        # Check result dictionary
        self.assertEqual(result["text"], "This is a tset")
        self.assertEqual(result["error_count"], 1)
        self.assertEqual(len(result["errors"]), 1)

        error = result["errors"][0]
        self.assertEqual(error["word"], "tset")
        self.assertIn("suggestions", error)
        self.assertGreater(len(error["suggestions"]), 0)

    def test_check_cas_with_pretokenized(self):
        """Test spell checking with pre-tokenized CAS."""
        cas = create_cas("This is a tset")
        tokenize_cas(cas)
        initial_token_count = len(get_tokens_from_cas(cas))

        cas, result = self.checker.check_cas(cas)

        # Should use existing tokens
        self.assertEqual(len(get_tokens_from_cas(cas)), initial_token_count)
        self.assertEqual(result["error_count"], 1)

    def test_check_cas_multiple_errors(self):
        """Test spell checking with multiple errors."""
        cas = create_cas("This is a tset of the speling checker")
        cas, result = self.checker.check_cas(cas)

        # Should find 2 errors
        self.assertEqual(result["error_count"], 2)
        words = [e["word"] for e in result["errors"]]
        self.assertIn("tset", words)
        self.assertIn("speling", words)

    def test_check_cas_no_errors(self):
        """Test spell checking with no errors."""
        cas = create_cas("This is a test")
        cas, result = self.checker.check_cas(cas)

        self.assertEqual(result["error_count"], 0)
        self.assertEqual(len(result["errors"]), 0)

    def test_check_text_still_works(self):
        """Test that original check_text method still works."""
        result = self.checker.check_text("This is a tset")

        self.assertEqual(result["error_count"], 1)
        self.assertEqual(result["errors"][0]["word"], "tset")


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility with existing Text-based API."""

    def setUp(self):
        """Set up test fixtures."""
        self.dictionary = {"this", "is", "a", "test"}
        self.detector = DictionaryErrorDetector(dictionary=self.dictionary)

    def test_text_api_still_works(self):
        """Test that original Text-based API still works."""
        from lespell.spellchecker.annotations import Text

        text = Text(content="This is a tset")
        text, errors = self.detector.detect(text)

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].word, "tset")

    def test_cas_and_text_give_same_results(self):
        """Test that CAS and Text APIs give equivalent results."""
        test_text = "This is a tset"

        # Test with Text
        from lespell.spellchecker.annotations import Text

        text = Text(content=test_text)
        text, text_errors = self.detector.detect(text)

        # Test with CAS
        cas = create_cas(test_text)
        cas, cas_errors = self.detector.detect_cas(cas)

        # Should find same errors
        self.assertEqual(len(text_errors), len(cas_errors))
        if text_errors:
            self.assertEqual(text_errors[0].word, cas_errors[0].word)
            self.assertEqual(text_errors[0].start, cas_errors[0].start)
            self.assertEqual(text_errors[0].end, cas_errors[0].end)


if __name__ == "__main__":
    unittest.main()
