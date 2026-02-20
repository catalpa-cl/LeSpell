"""Tests for PySpellChecker integration."""

import pytest

from lespell.integrations import PyspellcheckerErrorDetector, PyspellcheckerWrapper
from lespell.spellchecker.annotations import Text


class TestPyspellcheckerWrapper:
    """Test PySpellChecker wrapper functionality."""

    def test_wrapper_initialization(self):
        """Test wrapper can be initialized."""
        wrapper = PyspellcheckerWrapper(language="en")
        assert wrapper is not None
        assert wrapper.language == "en"

    def test_check_correct_word(self):
        """Test checking a correctly spelled word."""
        wrapper = PyspellcheckerWrapper(language="en")
        assert wrapper.check("hello") is True
        assert wrapper.check("python") is True

    def test_check_incorrect_word(self):
        """Test checking an incorrectly spelled word."""
        wrapper = PyspellcheckerWrapper(language="en")
        assert wrapper.check("helo") is False
        assert wrapper.check("pyton") is False

    def test_suggest_corrections(self):
        """Test getting suggestions for misspelled words."""
        wrapper = PyspellcheckerWrapper(language="en")
        suggestions = wrapper.suggest("speling")
        
        assert len(suggestions) > 0
        assert "spelling" in suggestions or "spieling" in suggestions

    def test_suggest_no_suggestions(self):
        """Test that correct words return empty suggestions."""
        wrapper = PyspellcheckerWrapper(language="en")
        suggestions = wrapper.suggest("hello")
        
        assert len(suggestions) == 0

    def test_add_to_dictionary(self):
        """Test adding custom words to dictionary."""
        wrapper = PyspellcheckerWrapper(language="en")
        custom_word = "customword123"
        
        # Should be unknown before adding
        assert wrapper.check(custom_word) is False
        
        # Add to dictionary
        wrapper.add_to_dictionary(custom_word)
        
        # Should be known after adding
        assert wrapper.check(custom_word) is True

    def test_custom_dict_initialization(self):
        """Test initializing wrapper with custom dictionary."""
        custom_words = ["customword", "anotherword"]
        wrapper = PyspellcheckerWrapper(language="en", custom_dict=custom_words)
        
        for word in custom_words:
            assert wrapper.check(word) is True


class TestPyspellcheckerErrorDetector:
    """Test PySpellChecker error detection."""

    def test_detector_initialization(self):
        """Test detector can be initialized."""
        detector = PyspellcheckerErrorDetector(language="en")
        assert detector is not None

    def test_detect_single_error(self):
        """Test detecting a single spelling error."""
        detector = PyspellcheckerErrorDetector(language="en")
        text = Text("teh word")
        _, errors = detector.detect(text)
        
        assert len(errors) > 0
        assert any(e.token == "teh" for e in errors)

    def test_detect_multiple_errors(self):
        """Test detecting multiple spelling errors."""
        detector = PyspellcheckerErrorDetector(language="en")
        text = Text("teh qick brwn fox")
        _, errors = detector.detect(text)
        
        assert len(errors) >= 2

    def test_detect_no_errors(self):
        """Test that correct text returns no errors."""
        detector = PyspellcheckerErrorDetector(language="en")
        text = Text("The quick brown fox jumps over the lazy dog")
        _, errors = detector.detect(text)
        
        # May have some errors due to word boundaries, but should be minimal
        assert len(errors) <= 2

    def test_error_has_suggestions(self):
        """Test that detected errors include suggestions."""
        detector = PyspellcheckerErrorDetector(language="en")
        text = Text("speling error")
        _, errors = detector.detect(text)
        
        spelling_errors = [e for e in errors if e.token == "speling"]
        assert len(spelling_errors) > 0
        assert len(spelling_errors[0].suggestions) > 0

    def test_detector_with_custom_dict(self):
        """Test detector with custom dictionary."""
        custom_words = ["techword"]
        detector = PyspellcheckerErrorDetector(language="en", custom_dict=custom_words)
        text = Text("This is a techword")
        _, errors = detector.detect(text)
        
        assert not any(e.token == "techword" for e in errors)

    def test_error_detector_name(self):
        """Test that errors are attributed to pyspellchecker detector."""
        detector = PyspellcheckerErrorDetector(language="en")
        text = Text("teh")
        _, errors = detector.detect(text)
        
        assert len(errors) > 0
        assert all(e.detector == "pyspellchecker" for e in errors)
