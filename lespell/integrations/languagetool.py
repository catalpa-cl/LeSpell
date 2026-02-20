"""LanguageTool integration wrapper."""

from typing import List

from lespell.integrations.base import SpellingCheckerBase

try:
    import language_tool_python

    HAS_LANGUAGE_TOOL = True
except ImportError:
    HAS_LANGUAGE_TOOL = False


class LanguageToolWrapper(SpellingCheckerBase):
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

    def check(self, word: str) -> bool:
        """Check if a single word is correctly spelled.

        Args:
            word: Word to check

        Returns:
            True if word is correct, False if there are errors
        """
        matches = self.tool.check(word)
        return len(matches) == 0

    def correct(self, word: str) -> str:
        """Get the best correction for a word.

        Args:
            word: Word to correct

        Returns:
            Best correction suggestion, or the original word if no suggestions
        """
        matches = self.tool.check(word)
        if matches and matches[0].replacements:
            return matches[0].replacements[0]
        return word

    def correct_text(self, text: str) -> str:
        """Correct a full text by fixing spelling and grammar errors.

        Args:
            text: Text to correct

        Returns:
            Corrected text
        """
        return self.tool.correct(text)

    def check_text(self, text: str) -> List[dict]:
        """Check text for errors and return detailed error information.

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
