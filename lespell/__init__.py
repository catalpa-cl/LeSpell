"""
LeSpell: A library for spelling error detection and analysis in learner corpora.
"""

from lespell.core import SpellingItem
from lespell.reader import SpellingReader
from lespell.writer import SpellingWriter

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "you@example.com"

__all__ = [
    "SpellingItem",
    "SpellingReader",
    "SpellingWriter",
    "data_prep",
    "analysis",
    "languagetool",
    "spellchecker",
]
