#!/usr/bin/env python3
"""PySpellChecker integration example with LeSpell."""

from lespell.integrations import PyspellcheckerErrorDetector
from lespell.spellchecker import (
    CostBasedRanker,
    LevenshteinCandidateGenerator,
    SpellingChecker,
)


def main():
    """Demonstrate spell checking using PySpellChecker integration."""
    # Create PySpellChecker detector
    detector = PyspellcheckerErrorDetector(language="en")

    # Create dictionary from common words for candidate generation
    dictionary = {
        "this", "is", "a", "test", "of", "the", "spelling", "checker",
        "quick", "brown", "fox", "jumps", "over", "lazy", "dog",
        "received", "package", "yesterday", "excellent", "communication", "skills",
    }

    # Create generator and ranker
    generator = LevenshteinCandidateGenerator(
        language="en",
        dictionary=dictionary,
        max_candidates=10,
    )
    ranker = CostBasedRanker()

    # Create spell checker with PySpellChecker detector
    checker = SpellingChecker(
        detector=detector,
        candidate_generators=[generator],
        ranker=ranker,
    )

    # Run spell check
    text = "This is a tset of the speling checker"
    result = checker.check_text(text)

    print(f"Text: {text}")
    print(f"Errors found: {result['error_count']}\n")

    for error in result["errors"]:
        print(f"'{error['word']}' at {error['start']}-{error['end']}")
        print(f"  Suggestions: {error['suggestions'][:3]}")


if __name__ == "__main__":
    main()
