"""Hunspell integration for error detection and candidate generation."""

from typing import List, Tuple, Optional
import re

from lespell.spellchecker.annotations import Text, Annotation
from lespell.spellchecker.errors import SpellingError
from lespell.spellchecker.detection import ErrorDetector

try:
    import hunspell
    HAS_HUNSPELL = True
except ImportError:
    HAS_HUNSPELL = False


class HunspellWrapper:
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
            raise ImportError(f"Failed to initialize Hunspell: {e}")

        self.dic_path = dic_path
        self.aff_path = aff_path
        self.language = language

    def check(self, word: str) -> bool:
        """Check if word is correctly spelled."""
        return self.spell.spell(word)

    def suggest(self, word: str) -> List[str]:
        """Get spelling suggestions for a misspelled word."""
        return self.spell.suggest(word)


class HunspellErrorDetector(ErrorDetector):
    """Detect errors using Hunspell dictionary."""

    def __init__(
        self,
        dic_path: Optional[str] = None,
        aff_path: Optional[str] = None,
        language: str = "en",
    ):
        """Initialize Hunspell error detector.

        Args:
            dic_path: Path to Hunspell .dic file (optional if language provided)
            aff_path: Path to Hunspell .aff file (optional if language provided)
            language: Language code for Hunspell (default: 'en')

        Raises:
            ImportError: If hunspell library is not installed
        """
        self.hunspell = HunspellWrapper(dic_path, aff_path, language)

    def detect(self, text: Text) -> Tuple[Text, List[SpellingError]]:
        """Detect errors using Hunspell."""
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

            # Check with Hunspell
            if not self.hunspell.check(token):
                annotation = Annotation(
                    type="spelling_error",
                    start=start,
                    end=end,
                    metadata={"token": token, "detector": "hunspell"},
                )
                text.add_annotation(annotation)

                error = SpellingError.from_annotation(annotation, text.content)
                errors.append(error)

        return text, errors
