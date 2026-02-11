"""Sophisticated spelling error detection and correction engine.

This module provides a modular spell checking system with three separate phases:
1. Error Detection: Identifies spelling errors in text
2. Correction Generation: Generates candidate corrections for errors
3. Ranking: Ranks candidates by quality

Each phase can be used independently or composed together.
"""

from lespell.spellchecker.annotations import Annotation, Pipeline, Text
from lespell.spellchecker.candidates import (
    CandidateGenerator,
    HunspellCandidateGenerator,
    LanguageToolCandidateGenerator,
    LevenshteinCandidateGenerator,
    MissingSpaceCandidateGenerator,
)
from lespell.spellchecker.detection import (
    ErrorDetector,
    DictionaryErrorDetector,
    CompositeErrorDetector,
)
from lespell.spellchecker.errors import SpellingError

from lespell.spellchecker.ranking import Ranker, CostBasedRanker
from lespell.spellchecker.spellchecker import SpellingChecker

__all__ = [
    # Annotations
    "Annotation",
    "Pipeline",
    "Text",
    # Error Detection
    "ErrorDetector",
    "DictionaryErrorDetector",
    "CompositeErrorDetector",
    "SpellingError",
    # Correction Generation
    "CandidateGenerator",
    "HunspellCandidateGenerator",
    "LanguageToolCandidateGenerator",
    "LevenshteinCandidateGenerator",
    "MissingSpaceCandidateGenerator",
    # Ranking
    "Ranker",
    "CostBasedRanker",
    # Main Orchestrator
    "SpellingChecker",
]

