"""Error detection components for spelling correction."""

import os
import re
from abc import ABC, abstractmethod
from typing import List, Tuple, Union

from cassis import Cas

from lespell.spellchecker.annotations import Annotation, Text
from lespell.spellchecker.cas_utils import (
    add_spelling_error,
    cas_to_text,
    get_tokens_from_cas,
    has_tokens,
    text_to_cas,
    tokenize_cas,
)
from lespell.spellchecker.errors import SpellingError


class ErrorDetector(ABC):
    """Abstract base class for error detection strategies."""

    @abstractmethod
    def detect(self, text: Text) -> Tuple[Text, List[SpellingError]]:
        """Detect spelling errors in preprocessed text.

        Args:
            text: Preprocessed Text object (with numeric, punctuation, capitalized annotations)

        Returns:
            Tuple of (annotated Text with spelling_error annotations, list of SpellingError objects)
        """
        pass

    def detect_cas(self, cas: Cas) -> Tuple[Cas, List[SpellingError]]:
        """Detect spelling errors in a CAS.

        Args:
            cas: CAS with text and optionally Token annotations

        Returns:
            Tuple of (CAS with SpellingAnomaly annotations, list of SpellingError objects)
        """
        # Convert CAS to Text for backward compatibility
        text = cas_to_text(cas)

        # Use existing detect method
        text, errors = self.detect(text)

        # Add spelling errors back to CAS
        for error in errors:
            add_spelling_error(cas, error.start, error.end)

        return cas, errors


class DictionaryErrorDetector(ErrorDetector):
    """Detect errors by checking against a word dictionary."""

    def __init__(self, dictionary=None):
        """Initialize dictionary error detector.

        Args:
            dictionary: Path-like, Set[str], or List[Set[str]].
                       Path-like: loads words from file (one per line)
                       Set[str]: uses directly
                       List[Set[str]]: merges all dictionaries

        Raises:
            ValueError: If dictionary not provided
            FileNotFoundError: If path doesn't exist
        """
        if dictionary is None:
            raise ValueError("dictionary parameter is required")

        merged = set()
        self.dictionary_path = None

        # Handle list of dictionaries
        if isinstance(dictionary, list):
            for d in dictionary:
                if isinstance(d, set):
                    merged.update(w.lower() for w in d)
                else:
                    raise TypeError(f"List items must be sets, got {type(d)}")
        # Handle path-like object
        elif isinstance(dictionary, (str, os.PathLike)):
            path = str(dictionary)
            if not os.path.exists(path):
                raise FileNotFoundError(f"Dictionary not found: {path}")
            with open(path, "r", encoding="utf-8") as f:
                merged.update(line.strip().lower() for line in f if line.strip())
            self.dictionary_path = path
        # Handle set
        elif isinstance(dictionary, set):
            merged.update(w.lower() for w in dictionary)
        else:
            raise TypeError(
                f"dictionary must be path-like, Set[str], or List[Set[str]], got {type(dictionary)}"
            )

        self.dictionary = merged

    def detect(self, text: Text) -> Tuple[Text, List[SpellingError]]:
        """Detect errors using dictionary lookup."""
        word_pattern = re.compile(r"^[a-zA-Z\'-]+$")
        tokens = text.get_tokens()
        errors = []

        for start, end, token in tokens:
            if not word_pattern.match(token):
                continue  # Not a word

            # Check if marked as excluded (numeric, punctuation, etc.)
            overlapping = text.get_overlapping_annotations(start, end)
            if any(a.type in {"numeric", "punctuation"} for a in overlapping):
                continue  # Excluded

            # Check if word is in dictionary
            if token.lower() in self.dictionary:
                continue  # Known word

            # Mark as spelling error
            annotation = Annotation(
                type="spelling_error",
                start=start,
                end=end,
                metadata={"token": token, "detector": "dictionary"},
            )
            text.add_annotation(annotation)

            error = SpellingError.from_annotation(annotation, text.content)
            errors.append(error)

        return text, errors

    def detect_cas(self, cas: Cas) -> Tuple[Cas, List[SpellingError]]:
        """Detect errors in CAS using dictionary lookup.

        Tokenizes the CAS if it doesn't have Token annotations.

        Args:
            cas: CAS with text and optionally Token annotations

        Returns:
            Tuple of (CAS with SpellingAnomaly annotations, list of SpellingError objects)
        """
        # Tokenize if needed
        if not has_tokens(cas):
            tokenize_cas(cas)

        # Get tokens from CAS
        word_pattern = re.compile(r"^[a-zA-Z\'-]+$")
        tokens = get_tokens_from_cas(cas)
        errors = []

        for start, end, token in tokens:
            if not word_pattern.match(token):
                continue  # Not a word

            # Check if word is in dictionary
            if token.lower() in self.dictionary:
                continue  # Known word

            # Add spelling error to CAS
            add_spelling_error(cas, start, end)

            # Create SpellingError object
            error = SpellingError(
                start=start,
                end=end,
                word=token,
                error_type="spelling_error",
                metadata={"detector": "dictionary"},
            )
            errors.append(error)

        return cas, errors


class CompositeErrorDetector(ErrorDetector):
    """Chain multiple error detectors with fallback behavior."""

    def __init__(self, detectors: List[ErrorDetector], use_first_match: bool = True):
        """Initialize composite error detector.

        Args:
            detectors: List of ErrorDetector instances to chain
            use_first_match: If True, use first detector that flags an error;
                           if False, require agreement from all detectors
        """
        if not detectors:
            raise ValueError("At least one detector required")
        self.detectors = detectors
        self.use_first_match = use_first_match

    def detect(self, text: Text) -> Tuple[Text, List[SpellingError]]:
        """Detect errors using chained detectors."""
        errors = []
        error_positions = set()

        for detector in self.detectors:
            text, detector_errors = detector.detect(text)

            for error in detector_errors:
                pos = (error.start, error.end)

                if self.use_first_match:
                    # Use first detector that flags this position
                    if pos not in error_positions:
                        errors.append(error)
                        error_positions.add(pos)
                else:
                    # Collect all detections (no filtering)
                    errors.append(error)

        return text, errors
