"""External spell checker integrations."""

from lespell.integrations.hunspell import HunspellErrorDetector, HunspellWrapper
from lespell.integrations.languagetool import (
    LanguageToolCorrector,
    LanguageToolDetector,
    LanguageToolWrapper,
)

__all__ = [
    "LanguageToolDetector",
    "LanguageToolCorrector",
    "LanguageToolWrapper",
    "HunspellErrorDetector",
    "HunspellWrapper",
]
