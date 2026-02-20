"""PySpellChecker integration for error detection and candidate generation."""

import re
from typing import List, Optional, Tuple

from spellchecker import SpellChecker

from lespell.spellchecker.annotations import Text
from lespell.spellchecker.detection import ErrorDetector
from lespell.spellchecker.errors import SpellingError


class PyspellcheckerWrapper:
    """Wrapper for PySpellChecker library initialization and usage."""

    def __init__(self, language: str = "en", custom_dict: Optional[List[str]] = None):
        """Initialize PySpellChecker wrapper.

        Args:
            language: Language code for PySpellChecker (default: 'en')
            custom_dict: Custom dictionary words to add (optional)
        """
        self.spell = SpellChecker(language=language)
        self.language = language

        # Add custom dictionary words if provided
        if custom_dict:
            self.spell.word_probability.load_words(custom_dict)

    def check(self, word: str) -> bool:
        """Check if word is correctly spelled.

        Args:
            word: Word to check

        Returns:
            True if word is correctly spelled, False otherwise
        """
        return word.lower() not in self.spell.unknown([word.lower()])

    def suggest(self, word: str, max_suggestions: int = 5) -> List[str]:
        """Get spelling suggestions for a misspelled word.

        Args:
            word: Misspelled word
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of spelling suggestions
        """
        unknown = self.spell.unknown([word.lower()])
        if not unknown:
            return []

        suggestions = self.spell.correction(word.lower())
        if suggestions:
            return [suggestions] if isinstance(suggestions, str) else list(suggestions)[:max_suggestions]
        return []

    def add_to_dictionary(self, word: str) -> None:
        """Add a word to the dictionary.

        Args:
            word: Word to add
        """
        self.spell.word_probability.load_words([word.lower()])


class PyspellcheckerErrorDetector(ErrorDetector):
    """Detect errors using PySpellChecker dictionary."""

    def __init__(self, language: str = "en", custom_dict: Optional[List[str]] = None):
        """Initialize PySpellChecker error detector.

        Args:
            language: Language code for PySpellChecker (default: 'en')
            custom_dict: Custom dictionary words to add (optional)
        """
        self.checker = PyspellcheckerWrapper(language, custom_dict)

    def detect(self, text: Text) -> Tuple[Text, List[SpellingError]]:
        """Detect errors using PySpellChecker.

        Args:
            text: Text object to detect errors in

        Returns:
            Tuple of (text, list of SpellingError objects)
        """
        word_pattern = re.compile(r"^[a-zA-Z\'-]+$")
        tokens = text.get_tokens()
        errors = []

        for start, end, token in tokens:
            if not word_pattern.match(token):
                continue  # Not a word

            # Check if marked as known or excluded
            overlapping = text.get_overlapping_annotations(start, end)
            if any(
                a.type in {"numeric", "punctuation"}
                for a in overlapping
            ):
                continue  # Excluded

            # Check spelling
            if not self.checker.check(token):
                suggestions = self.checker.suggest(token)
                error = SpellingError(
                    start=start,
                    end=end,
                    token=token,
                    suggestions=suggestions,
                    detector="pyspellchecker",
                )
                errors.append(error)

        return text, errors
