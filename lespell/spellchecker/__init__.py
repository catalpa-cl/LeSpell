"""Sophisticated spelling error detection and correction engine.

This module provides a modular spell checking system with multiple candidate
generation strategies and ranking mechanisms.
"""

from lespell.spellchecker.annotations import Annotation, Pipeline, Text
from lespell.spellchecker.candidates import (
    CandidateGenerator,
    CandidateEnsemble,
    HunspellCandidateGenerator,
    LevenshteinCandidateGenerator,
    MissingSpaceCandidateGenerator,
)
from lespell.spellchecker.preprocessing import PreprocessingPipeline, SimplePreprocessor
from lespell.spellchecker.ranking import Ranker, CostBasedRanker
from lespell.spellchecker.spellchecker import SpellingChecker

__all__ = [
    "Annotation",
    "Pipeline",
    "Text",
    "CandidateGenerator",
    "CandidateEnsemble",
    "HunspellCandidateGenerator",
    "LevenshteinCandidateGenerator",
    "MissingSpaceCandidateGenerator",
    "PreprocessingPipeline",
    "SimplePreprocessor",
    "Ranker",
    "CostBasedRanker",
    "SpellingChecker",
]
