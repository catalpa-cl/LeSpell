"""Tests for LanguageTool integration."""

import pytest

from lespell.languagetool import LanguageToolCorrector, LanguageToolDetector

# Skip all tests if language-tool-python is not installed
pytest.importorskip("language_tool_python")


class TestLanguageToolDetector:
    """Test LanguageTool error detection."""

    def test_detector_initialization(self):
        """Test detector can be initialized."""
        detector = LanguageToolDetector(language="en")
        assert detector is not None

    def test_detect_simple_error(self):
        """Test detecting a simple spelling error."""
        detector = LanguageToolDetector(language="en")
        errors = detector.detect_errors("This is a tst.")

        assert len(errors) > 0

    def test_detect_grammar_error(self):
        """Test detecting a grammar error."""
        detector = LanguageToolDetector(language="en")
        errors = detector.detect_errors("She go to school.")

        assert len(errors) > 0


class TestLanguageToolCorrector:
    """Test LanguageTool error correction."""

    def test_corrector_initialization(self):
        """Test corrector can be initialized."""
        corrector = LanguageToolCorrector(language="en")
        assert corrector is not None

    def test_correct_text(self):
        """Test correcting text."""
        corrector = LanguageToolCorrector(language="en")
        corrected = corrector.correct_text("This is a tst.")

        # Should be corrected
        assert corrected is not None
