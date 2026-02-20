"""PySpellChecker integration wrapper."""

import re
from typing import List, Optional

from spellchecker import SpellChecker

from lespell.integrations.base import SpellingCheckerBase


class PyspellcheckerWrapper(SpellingCheckerBase):
    """Wrapper for PySpellChecker library initialization and usage."""

    def __init__(self, language: str = "en", custom_dict: Optional[List[str]] = None):
        self.spell = SpellChecker(language=language)
        self.language = language

        # Add custom dictionary words if provided
        if custom_dict:
            self.spell.word_frequency.load_words(custom_dict)

    def check(self, word: str) -> bool:
        """Check if word is correctly spelled.

        Args:
            word: Word to check

        Returns:
            True if word is correct, False otherwise
        """
        return word.lower() not in self.spell.unknown([word.lower()])

    def correct(self, word: str) -> str:
        """Get the best correction for a misspelled word.

        Args:
            word: Word to correct

        Returns:
            Best correction suggestion, or the original word if no suggestions
        """
        unknown = self.spell.unknown([word.lower()])
        if not unknown:
            return word

        suggestion = self.spell.correction(word.lower())
        return suggestion if suggestion else word

    def correct_text(self, text: str) -> str:
        """Correct a full text by fixing spelling errors.

        Args:
            text: Text to correct

        Returns:
            Corrected text
        """
        # Split text into tokens (words and non-words), keeping delimiters
        tokens = re.split(r"([a-zA-Z\'-]+)", text)
        
        # Correct only the word tokens (odd indices after split)
        corrected_tokens = [
            self.correct(token) if i % 2 == 1 else token
            for i, token in enumerate(tokens)
        ]
        
        return "".join(corrected_tokens)
