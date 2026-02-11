"""Tests for error detection components."""

import os
import tempfile
import unittest

from lespell.spellchecker import (
    CompositeErrorDetector,
    DictionaryErrorDetector,
    SpellingError,
)
from lespell.spellchecker.annotations import Text


def create_test_dictionary_file():
    """Create temporary test dictionary file."""
    fd, path = tempfile.mkstemp(suffix=".txt", text=True)
    with os.fdopen(fd, "w") as f:
        f.write("this\nis\na\ntest\nof\nthe\nspelling\nchecker\nwith\nnumbers\n")
    return path


class TestDictionaryErrorDetector(unittest.TestCase):
    """Test DictionaryErrorDetector."""

    def setUp(self):
        """Set up test fixtures."""
        self.dict_path = create_test_dictionary_file()
        self.detector = DictionaryErrorDetector(self.dict_path)

    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.dict_path):
            os.remove(self.dict_path)

    def test_detector_initialization(self):
        """Test detector initialization."""
        self.assertIsNotNone(self.detector.dictionary)
        self.assertEqual(len(self.detector.dictionary), 10)

    def test_detect_known_words(self):
        """Test detection returns no errors for known words."""
        text = Text("This is a test")
        text, errors = self.detector.detect(text)

        self.assertEqual(len(errors), 0)

    def test_detect_unknown_words(self):
        """Test detection identifies unknown words."""
        text = Text("This is a tset")
        text, errors = self.detector.detect(text)

        self.assertGreater(len(errors), 0)
        self.assertTrue(any(e.word == "tset" for e in errors))

    def test_detect_returns_annotations(self):
        """Test that detect returns both annotations and errors."""
        text = Text("This is a tset")
        text, errors = self.detector.detect(text)

        # Check annotations
        spelling_errors = text.get_annotations_by_type("spelling_error")
        self.assertGreater(len(spelling_errors), 0)

        # Check errors
        self.assertEqual(len(errors), len(spelling_errors))

    def test_spelling_error_structure(self):
        """Test SpellingError objects have correct structure."""
        text = Text("tset")
        text, errors = self.detector.detect(text)

        self.assertEqual(len(errors), 1)
        error = errors[0]

        self.assertIsInstance(error, SpellingError)
        self.assertEqual(error.word, "tset")
        self.assertEqual(error.start, 0)
        self.assertEqual(error.end, 4)
        self.assertEqual(error.error_type, "spelling_error")

    def test_detector_not_found(self):
        """Test that detector raises error for nonexistent dictionary."""
        with self.assertRaises(FileNotFoundError):
            DictionaryErrorDetector("/nonexistent/path/dictionary.txt")

    def test_detect_with_punctuation(self):
        """Test that punctuation is not marked as error."""
        text = Text("This, is. a test!")
        text, errors = self.detector.detect(text)

        # Punctuation tokens should not be in errors
        self.assertEqual(len(errors), 0)

    def test_detect_with_numerics(self):
        """Test that numerics are not marked as errors."""
        text = Text("Test 123 with numbers 456")
        text, errors = self.detector.detect(text)

        self.assertEqual(len(errors), 0)


class TestCompositeErrorDetector(unittest.TestCase):
    """Test CompositeErrorDetector."""

    def setUp(self):
        """Set up test fixtures."""
        self.dict_path = create_test_dictionary_file()

    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.dict_path):
            os.remove(self.dict_path)

    def test_composite_initialization(self):
        """Test CompositeErrorDetector initialization."""
        detector1 = DictionaryErrorDetector(self.dict_path)
        composite = CompositeErrorDetector([detector1])

        self.assertEqual(len(composite.detectors), 1)

    def test_composite_requires_detectors(self):
        """Test that composite requires at least one detector."""
        with self.assertRaises(ValueError):
            CompositeErrorDetector([])

    def test_composite_with_multiple_detectors(self):
        """Test composite with multiple detectors."""
        detector1 = DictionaryErrorDetector(self.dict_path)
        detector2 = DictionaryErrorDetector(self.dict_path)

        composite = CompositeErrorDetector([detector1, detector2])

        text = Text("tset")
        text, errors = composite.detect(text)

        # With use_first_match=True, should only report once
        self.assertEqual(len(errors), 1)


class TestSpellingError(unittest.TestCase):
    """Test SpellingError data class."""

    def test_spelling_error_creation(self):
        """Test SpellingError creation."""
        error = SpellingError(
            start=0,
            end=4,
            word="tset",
            context="This is a tset",
        )

        self.assertEqual(error.start, 0)
        self.assertEqual(error.end, 4)
        self.assertEqual(error.word, "tset")
        self.assertEqual(error.context, "This is a tset")

    def test_spelling_error_repr(self):
        """Test SpellingError string representation."""
        error = SpellingError(start=10, end=14, word="test")
        repr_str = repr(error)

        self.assertIn("SpellingError", repr_str)
        self.assertIn("10-14", repr_str)
        self.assertIn("test", repr_str)


if __name__ == "__main__":
    unittest.main()

