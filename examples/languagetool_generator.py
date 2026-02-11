#!/usr/bin/env python3
"""Example using LanguageTool candidate generator."""

from lespell.spellchecker import (
    SpellingChecker,
    LevenshteinCandidateGenerator,
    LanguageToolCandidateGenerator,
    CostBasedRanker,
    DictionaryErrorDetector,
)
from lespell.integrations import LanguageToolWrapper


def main():
    """Demonstrate spell checking with LanguageTool candidates."""
    # Set up dictionary
    dictionary = {
        "this", "is", "a", "test", "of", "the", "spelling", "checker",
        "quick", "brown", "fox", "jumps", "over", "lazy", "dog",
        "received", "package", "yesterday", "excellent", "communication", "skills",
    }

    # Create detector
    detector = DictionaryErrorDetector(dictionary=dictionary)

    # Initialize LanguageTool wrapper
    try:
        lt = LanguageToolWrapper(language="en")
        
        # Create spell checker with both Levenshtein and LanguageTool generators
        checker = SpellingChecker(
            detector=detector,
            candidate_generators=[
                LevenshteinCandidateGenerator(
                    language="en",
                    dictionary=dictionary,
                    max_candidates=10,
                ),
                LanguageToolCandidateGenerator(lt),
            ],
            ranker=CostBasedRanker(),
        )

        # Run spell check
        text = "This is a tset of the speling checker"
        result = checker.check_text(text)

        print(f"Text: {text}")
        print(f"Errors found: {result['error_count']}\n")

        for error in result["errors"]:
            print(f"'{error['word']}' at {error['start']}-{error['end']}")
            print(f"  Suggestions: {error['suggestions'][:3]}")
            print(f"  Methods: {error['methods'][:3]}\n")

    except ImportError as e:
        print(f"LanguageTool not available: {e}")
        print("Install with: pip install language-tool-python")


if __name__ == "__main__":
    main()
