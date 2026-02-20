"""Tests for PySpellChecker integration."""

import pytest

from lespell.integrations import PyspellcheckerWrapper


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

    def test_correct_word(self):
        """Test getting best correction for a misspelled word."""
        wrapper = PyspellcheckerWrapper(language="en")
        correction = wrapper.correct("speling")
        
        assert correction == "spelling"
        assert isinstance(correction, str)

    def test_correct_correct_word(self):
        """Test that correct words return themselves."""
        wrapper = PyspellcheckerWrapper(language="en")
        correction = wrapper.correct("hello")
        
        assert correction == "hello"

    def test_custom_dict_initialization(self):
        """Test initializing wrapper with custom dictionary."""
        custom_words = ["customword", "anotherword"]
        wrapper = PyspellcheckerWrapper(language="en", custom_dict=custom_words)
        
        for word in custom_words:
            assert wrapper.check(word) is True

    def test_correct_text(self):
        """Test correcting full text."""
        wrapper = PyspellcheckerWrapper(language="en")
        text = "This is a speling eror"
        corrected = wrapper.correct_text(text)
        
        # Should be a string
        assert isinstance(corrected, str)
        # Should contain corrected words
        assert "spelling" in corrected.lower()
        assert "error" in corrected.lower()
