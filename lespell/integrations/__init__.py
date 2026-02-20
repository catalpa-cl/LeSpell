"""External spell checker integrations."""

from lespell.integrations.base import SpellingCheckerBase

__all__ = ["SpellingCheckerBase"]

# Optional wrappers - only imported if their dependencies are available
try:
    from lespell.integrations.pyspellchecker import PyspellcheckerWrapper
    __all__.append("PyspellcheckerWrapper")
except ImportError:
    pass

try:
    from lespell.integrations.hunspell import HunspellWrapper
    __all__.append("HunspellWrapper")
except ImportError:
    pass

try:
    from lespell.integrations.languagetool import LanguageToolWrapper
    __all__.append("LanguageToolWrapper")
except ImportError:
    pass
