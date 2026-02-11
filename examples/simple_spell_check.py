#!/usr/bin/env python3
"""Simple spell checking example with LeSpell."""

from lespell.spellchecker import (
    SpellingChecker,
    LevenshteinCandidateGenerator,
    CostBasedRanker,
    DictionaryErrorDetector,
)


def main():
    """Demonstrate basic spell checking."""
    # Set up dictionary
    dictionary = {
        "this", "is", "a", "test", "of", "the", "spelling", "checker",
        "quick", "brown", "fox", "jumps", "over", "lazy", "dog",
        "received", "package", "yesterday", "excellent", "communication", "skills",
    }

    # Create detector
    detector = DictionaryErrorDetector(dictionary=dictionary)

    # Create generator and ranker
    generator = LevenshteinCandidateGenerator(
        language="en",
        dictionary=dictionary,
        max_candidates=10,
    )
    ranker = CostBasedRanker()

    # Create spell checker
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
