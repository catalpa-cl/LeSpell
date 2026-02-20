"""Hunspell integration wrapper."""

import re
from typing import List, Optional

from lespell.integrations.base import SpellingCheckerBase

try:
    import hunspell
    HAS_HUNSPELL = True
except ImportError:
    HAS_HUNSPELL = False


class HunspellWrapper(SpellingCheckerBase):
    """Wrapper for Hunspell library initialization and usage."""

    def __init__(
        self,
        dic_path: Optional[str] = None,
        aff_path: Optional[str] = None,
        language: str = "en",
    ):
        """Initialize Hunspell wrapper.

        Args:
            dic_path: Path to Hunspell .dic file (optional if language provided)
            aff_path: Path to Hunspell .aff file (optional if language provided)
            language: Language code for Hunspell (default: 'en')

        Raises:
            ImportError: If hunspell library is not installed
        """
        if not HAS_HUNSPELL:
            raise ImportError(
                "hunspell library required. "
                "Install with: pip install hunspell"
            )

        try:
            if dic_path and aff_path:
                self.spell = hunspell.HunSpell(dic_path, aff_path)
            else:
                self.spell = hunspell.HunSpell(language)
        except Exception as e:
            raise ImportError(f"Failed to initialize Hunspell: {e}") from e

        self.dic_path = dic_path
        self.aff_path = aff_path
        self.language = language

    def check(self, word: str) -> bool:
        """Check if word is correctly spelled.

        Args:
            word: Word to check

        Returns:
            True if word is correct, False otherwise
        """
        return self.spell.spell(word)

    def correct(self, word: str) -> str:
        """Get the best correction for a misspelled word.

        Args:
            word: Word to correct

        Returns:
            Best correction suggestion, or the original word if no suggestions
        """
        suggestions = self.spell.suggest(word)
        return suggestions[0] if suggestions else word

    def correct_text(self, text: str) -> str:
        """Correct a full text by fixing spelling errors.

        Args:
            text: Text to correct

        Returns:
            Corrected text
        """
        word_pattern = re.compile(r"[a-zA-Z\'-]+")
        corrected_text = text
        offset = 0

        for match in word_pattern.finditer(text):
            word = match.group()
            corrected_word = self.correct(word)
            
            if corrected_word != word:
                start = match.start() + offset
                end = start + len(word)
                corrected_text = corrected_text[:start] + corrected_word + corrected_text[end:]
                offset += len(corrected_word) - len(word)

        return corrected_text
