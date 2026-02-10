#!/usr/bin/env python3
"""Simple example: Basic spell checking with LeSpell."""

from lespell.spellchecker import (
    SpellingChecker,
    LevenshteinCandidateGenerator,
    CostBasedRanker,
)


def create_simple_dictionary():
    """Create a simple dictionary for demonstration."""
    return {
        "this", "is", "a", "test", "of", "the", "spelling", "checker",
        "quick", "brown", "fox", "jumps", "over", "lazy", "dog",
        "received", "package", "yesterday", "excellent", "communication", "skills",
    }


def main():
    """Run a simple spell check example."""
    print("=" * 60)
    print("LeSpell - Simple Spell Checker Example")
    print("=" * 60)

    # Initialize spell checker with Levenshtein distance generator
    print("\n1. Initializing spell checker...")
    print("   Note: Spell checkers REQUIRE a dictionary to work")
    print("   LevenshteinCandidateGenerator compares against every dictionary word using edit distance")
    
    # Load dictionary
    dictionary = create_simple_dictionary()
    print(f"   ✓ Dictionary loaded with {len(dictionary)} words")
    
    checker = SpellingChecker(
        candidate_generators=[
            LevenshteinCandidateGenerator(
                language="en",
                dictionary=dictionary,
                substitution_weight=1.0,
                deletion_weight=1.0,
                insertion_weight=1.0,
                max_candidates=10,
            )
        ],
        ranker=CostBasedRanker(),
    )
    
    # Load dictionary into generator
    checker.ensemble.generators[0].dictionary = dictionary
    print("   ✓ Spell checker ready")

    # Example 1: Demonstrate candidate generation for misspelled words
    print("\n2. Testing candidate generation...")
    generator = checker.ensemble.generators[0]
    
    test_words = [
        ("tset", "test"),
        ("speling", "spelling"),
        ("qwick", "quick"),
    ]
    
    for misspelled, expected in test_words:
        candidates = generator.generate(misspelled)
        if candidates:
            top_match = candidates[0][0]
            status = "✓" if top_match == expected else "✗"
            print(f"   {status} '{misspelled}' → top: '{top_match}' (expected: '{expected}')")
            print(f"       All suggestions: {[f'{w} ({c:.2f})' for w, c in candidates[:3]]}")
        else:
            print(f"   ✗ '{misspelled}' → NO CANDIDATES (dictionary not loaded!)")

    # Example 2: Demonstrate why dictionaries are essential
    print("\n3. Demonstrating mandatory dictionary requirement...")
    print("   Attempting to create generator WITHOUT dictionary:")
    try:
        generator_no_dict = LevenshteinCandidateGenerator(
            language="en",
            max_candidates=10,
        )
        print("   ✗ ERROR: Should have raised ValueError!")
    except ValueError as e:
        print(f"   ✓ Correctly raised error: {str(e)[:60]}...")
    
    print("\n   Creating generator WITH dictionary:")
    generator_with_dict = LevenshteinCandidateGenerator(
        language="en",
        dictionary=dictionary,
        max_candidates=10,
    )
    print(f"   ✓ Successfully created with {len(generator_with_dict.dictionary)} words")
    
    print("\n   Testing 'tset' WITH dictionary:")
    candidates = generator_with_dict.generate("tset")
    if candidates:
        print(f"   ✓ Candidates: {[f'{w} ({c:.2f})' for w, c in candidates[:3]]}")
    else:
        print(f"   ✗ No candidates")

    print("\n" + "=" * 60)
    print("Key Lesson: Spell Checkers Require Dictionaries")
    print("=" * 60)
    print("✓ Architecture enforces mandatory dictionaries at init time")
    print("✓ Prevents silent failures and ensures spell checkers work correctly")
    print("✓ Supports loading from file OR passing pre-loaded dictionary")
    print("\nAll dictionary-based spell checkers require this!")
    print("=" * 60)


if __name__ == "__main__":
    main()
