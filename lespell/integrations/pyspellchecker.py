"""PySpellChecker integration wrapper."""

import re
from typing import List, Optional

from spellchecker import SpellChecker

from lespell.integrations.base import SpellingCheckerBase

# We want to matches as a "word" any run of letters.
# Run is defined unicode-aware, it covers umlauts,
# accented characters, etc.), optionally joined by single apostrophes
# or hyphens (e.g. "don't", "well-known"). 
# We use ``[^\W\d_]`` instead of ``[a-zA-Z]`` so words in non-ASCII alphabets 
# aren't split  into chunks at every umlaut, which would feed bits 
# like "m"/"ö"/"gliche" to the spell checker.
_WORD_RE = re.compile(r"[^\W\d_]+(?:['\-][^\W\d_]+)*", re.UNICODE)


def _reapply_case(original: str, suggestion: str) -> str:
    """Cast ``suggestion`` into the same casing pattern as ``original``.

    The pyspellchecker normalises everything to lowercase internally and
    returns lowercase corrections, which removes German noun
    capitalisation and sentence-initial caps. 
    We re-construct the original casing pattern so that 
    - all-caps stays all-caps, 
    - Title-case stays Title-case, 
    - everything else passes through as-is.
    """
    if not suggestion:
        return original
    if original.isupper() and len(original) > 1:
        return suggestion.upper()
    if original[:1].isupper() and original[1:].islower():
        return suggestion[:1].upper() + suggestion[1:]
    return suggestion


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
        if not suggestion:
            return word
        return _reapply_case(word, suggestion)

    def correct_text(self, text: str) -> str:
        """Correct a full text by fixing spelling errors.

        Args:
            text: Text to correct

        Returns:
            Corrected text
        """
        # Skip all-caps tokens of length > 1 (likely acronyms — pyspell
        # has no reliable signal to "correct" them).
        def _fix(match: "re.Match[str]") -> str:
            word = match.group(0)
            if word.isupper() and len(word) > 1:
                return word
            return self.correct(word)

        return _WORD_RE.sub(_fix, text)
