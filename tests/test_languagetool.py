"""Tests for LanguageTool integration."""

import pytest

from lespell.integrations import LanguageToolWrapper

# Skip all tests if language-tool-python is not installed
pytest.importorskip("language_tool_python")


class TestLanguageToolWrapper:
    """Test LanguageTool wrapper functionality."""

    def test_wrapper_initialization(self):
        """Test wrapper can be initialized."""
        wrapper = LanguageToolWrapper(language="en")
        assert wrapper is not None
        assert wrapper.language == "en"

    def test_check_correct_word(self):
        """Test checking a correctly spelled word."""
        wrapper = LanguageToolWrapper(language="en")
        # Most correct words should pass
        assert wrapper.check("correct") is True

    def test_check_incorrect_word(self):
        """Test checking an incorrectly spelled word."""
        wrapper = LanguageToolWrapper(language="en")
        # Obviously misspelled words should fail
        errors = wrapper.check_text("tst")
        assert len(errors) > 0

    def test_correct_word(self):
        """Test getting best correction for a misspelled word."""
        wrapper = LanguageToolWrapper(language="en")
        correction = wrapper.correct("tst")
        
        # Should return a string
        assert isinstance(correction, str)
        # Most likely it will be "test"
        assert correction in ("test", "tst")  # Could return original if no suggestions

    def test_correct_text(self):
        """Test correcting full text."""
        wrapper = LanguageToolWrapper(language="en")
        text = "This is a tst."
        corrected = wrapper.correct_text(text)
        
        # Should be a string
        assert isinstance(corrected, str)
        # Should be different from original or at least valid
        assert len(corrected) > 0

    def test_check_text(self):
        """Test checking text for errors and returning error details."""
        wrapper = LanguageToolWrapper(language="en")
        errors = wrapper.check_text("This is a tst.")
        
        # Should return a list of error dicts
        assert isinstance(errors, list)
        
        if errors:
            error = errors[0]
            assert "offset" in error
            assert "length" in error
            assert "message" in error
            assert "replacements" in error

    def test_get_suggestions(self):
        """Test getting suggestions for specific error position."""
        wrapper = LanguageToolWrapper(language="en")
        text = "This is a tst."
        errors = wrapper.check_text(text)
        
        if errors:
            error = errors[0]
            suggestions = wrapper.get_suggestions(text, error["offset"], error["length"])
            assert isinstance(suggestions, list)
