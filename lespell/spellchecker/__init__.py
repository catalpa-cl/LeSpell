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
from lespell.spellchecker.cas_utils import (
    add_spelling_error,
    cas_to_text,
    create_cas,
    get_spelling_errors,
    get_tokens_from_cas,
    has_tokens,
    text_to_cas,
    tokenize_cas,
)
from lespell.spellchecker.detection import (
    CompositeErrorDetector,
    DictionaryErrorDetector,
    ErrorDetector,
)
from lespell.spellchecker.errors import SpellingError
from lespell.spellchecker.ranking import CostBasedRanker, MaskedLanguageModelRanker, Ranker
from lespell.spellchecker.spellchecker import SpellingChecker

__all__ = [
    # Annotations
    "Annotation",
    "Pipeline",
    "Text",
    # CAS utilities
    "create_cas",
    "tokenize_cas",
    "cas_to_text",
    "text_to_cas",
    "has_tokens",
    "get_tokens_from_cas",
    "add_spelling_error",
    "get_spelling_errors",
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
    "MaskedLanguageModelRanker",
    # Main Orchestrator
    "SpellingChecker",
]

