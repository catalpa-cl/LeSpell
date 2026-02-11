"""LanguageTool integration for error detection and correction."""

from typing import Any, List, Optional, Dict

from lespell.io import SpellingItem

try:
    import language_tool_python

    HAS_LANGUAGE_TOOL = True
except ImportError:
    HAS_LANGUAGE_TOOL = False


class LanguageToolWrapper:
    """Wrapper for LanguageTool library initialization and usage."""

    def __init__(self, language: str = "en"):
        """Initialize LanguageTool wrapper.

        Args:
            language: Language code (e.g., 'en', 'de', 'it')

        Raises:
            ImportError: If language-tool-python is not installed
        """
        if not HAS_LANGUAGE_TOOL:
            raise ImportError(
                "language-tool-python is required. "
                "Install with: pip install language-tool-python"
            )

        self.language = language
        self.tool = language_tool_python.LanguageTool(language)

    def check(self, text: str) -> List[Dict[str, Any]]:
        """Check text for errors.

        Args:
            text: Text to check

        Returns:
            List of error dictionaries with keys:
                - offset: Character offset of error
                - length: Length of error
                - message: Error message
                - replacements: List of suggested corrections
        """
        matches = self.tool.check(text)

        errors = []
        for match in matches:
            errors.append(
                {
                    "offset": match.offset,
                    "length": match.length,
                    "message": match.message,
                    "replacements": match.replacements[:3] if match.replacements else [],
                }
            )

        return errors

    def correct(self, text: str) -> str:
        """Automatically correct text.

        Args:
            text: Text to correct

        Returns:
            Corrected text
        """
        return self.tool.correct(text)

    def get_suggestions(self, text: str, offset: int, length: int) -> List[str]:
        """Get suggestions for error at given position.

        Args:
            text: Full text
            offset: Character offset of error
            length: Length of error

        Returns:
            List of correction suggestions or empty list if no suggestions
        """
        matches = self.tool.check(text)

        for match in matches:
            if match.offset == offset and match.length == length:
                return match.replacements if match.replacements else []

        return []


class LanguageToolDetector:
    """Detects errors using LanguageTool API."""

    def __init__(self, languagetool_wrapper: LanguageToolWrapper):
        """Initialize detector.

        Args:
            languagetool_wrapper: Configured LanguageToolWrapper instance
        """
        self.tool = languagetool_wrapper

    def detect_errors(self, text: str) -> List[dict]:
        """Detect errors in text.

        Args:
            text: Text to check

        Returns:
            List of error dictionaries with keys:
                - offset: Character offset of error
                - length: Length of error
                - message: Error message
                - replacements: List of suggested corrections
        """
        return self.tool.check(text)

    def extract_error_items(self, items: List[SpellingItem]) -> List[dict]:
        """Extract errors from SpellingItem list.

        Args:
            items: List of SpellingItem objects

        Returns:
            List of detected errors with context
        """
        all_errors = []

        for item in items:
            errors = self.detect_errors(item.text)

            for error in errors:
                all_errors.append(
                    {
                        "corpus": item.corpus_name,
                        "text_id": item.text_id,
                        "offset": error["offset"],
                        "length": error["length"],
                        "error_text": item.text[
                            error["offset"] : error["offset"] + error["length"]
                        ],
                        "message": error["message"],
                        "suggestions": error["replacements"],
                    }
                )

        return all_errors


class LanguageToolCorrector:
    """Corrects errors using LanguageTool suggestions."""

    def __init__(self, languagetool_wrapper: LanguageToolWrapper):
        """Initialize corrector.

        Args:
            languagetool_wrapper: Configured LanguageToolWrapper instance
        """
        self.tool = languagetool_wrapper

    def correct_text(self, text: str) -> str:
        """Automatically correct text.

        Args:
            text: Text to correct

        Returns:
            Corrected text
        """
        return self.tool.correct(text)

    def get_best_correction(self, text: str, offset: int, length: int) -> Optional[str]:
        """Get best correction for error at given position.

        Args:
            text: Full text
            offset: Character offset of error
            length: Length of error

        Returns:
            Best correction suggestion or None if no suggestions
        """
        suggestions = self.tool.get_suggestions(text, offset, length)
        return suggestions[0] if suggestions else None

    def correct_items(self, items: List[SpellingItem]) -> List[SpellingItem]:
        """Apply LanguageTool corrections to items.

        Args:
            items: List of SpellingItem objects

        Returns:
            List of SpellingItem objects with LT corrections applied
        """
        corrected_items = []

        for item in items:
            corrected_text = self.correct_text(item.text)

            corrected_item = SpellingItem(
                corpus_name=item.corpus_name,
                text_id=item.text_id + "_lt_corrected",
                text=corrected_text,
                corrections=item.corrections.copy(),
                correction_error_types=item.correction_error_types.copy(),
                grammar_corrections=item.grammar_corrections.copy(),
            )

            corrected_items.append(corrected_item)

        return corrected_items

        Returns:
            List of SpellingItem objects with LT corrections applied
        """
        corrected_items = []

        for item in items:
            corrected_text = self.correct_text(item.text)

            corrected_item = SpellingItem(
                corpus_name=item.corpus_name,
                text_id=item.text_id + "_lt_corrected",
                text=corrected_text,
                corrections=item.corrections.copy(),
                correction_error_types=item.correction_error_types.copy(),
                grammar_corrections=item.grammar_corrections.copy(),
            )

            corrected_items.append(corrected_item)

        return corrected_items
