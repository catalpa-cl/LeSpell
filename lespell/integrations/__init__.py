"""External spell checker integrations."""

from lespell.integrations.languagetool import (
    LanguageToolCorrector,
    LanguageToolDetector,
    LanguageToolWrapper,
)
from lespell.integrations.hunspell import HunspellErrorDetector, HunspellWrapper

__all__ = [
    "LanguageToolDetector",
    "LanguageToolCorrector",
    "LanguageToolWrapper",
    "HunspellErrorDetector",
    "HunspellWrapper",
]
