#!/usr/bin/env python3
"""Example demonstrating CAS-based spell checking with LeSpell.

This example shows how to use the new CAS (Common Analysis Structure) API
with dkpro-cassis for spelling correction. The CAS API allows you to:

1. Use plain text (LeSpell tokenizes internally)
2. Use pre-tokenized CAS (provide your own tokens)
3. Get results as CAS with SpellingAnomaly annotations
"""

from lespell.spellchecker import (
    CostBasedRanker,
    DictionaryErrorDetector,
    LevenshteinCandidateGenerator,
    SpellingChecker,
    create_cas,
    get_spelling_errors,
    tokenize_cas,
)


def main():
    """Demonstrate CAS-based spell checking."""
    # Set up dictionary
    dictionary = {
        "this",
        "is",
        "a",
        "test",
        "of",
        "the",
        "spelling",
        "checker",
        "with",
        "cas",
        "support",
        "quick",
        "brown",
        "fox",
        "jumps",
        "over",
        "lazy",
        "dog",
    }

    # Create detector, generator, and ranker
    detector = DictionaryErrorDetector(dictionary=dictionary)
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

    print("=" * 70)
    print("Example 1: Check text with automatic tokenization")
    print("=" * 70)

    # Create CAS from plain text (will be tokenized automatically)
    text1 = "This is a tset of the speling checker"
    cas1 = create_cas(text1)

    # Check spelling (tokenizes automatically if needed)
    cas1, result1 = checker.check_cas(cas1)

    print(f"\nInput: {text1}")
    print(f"Errors found: {result1['error_count']}\n")

    for error in result1["errors"]:
        print(f"  '{error['word']}' at {error['start']}-{error['end']}")
        print(f"    Suggestions: {', '.join(error['suggestions'][:3])}\n")

    # Show CAS annotations
    print("CAS SpellingAnomaly annotations:")
    for begin, end, text in get_spelling_errors(cas1):
        print(f"  - '{text}' at {begin}-{end}")

    print("\n" + "=" * 70)
    print("Example 2: Use pre-tokenized CAS")
    print("=" * 70)

    # Create CAS and tokenize it before spell checking
    text2 = "The qwick brown fox jumps over the lazi dog"
    cas2 = create_cas(text2)
    tokenize_cas(cas2)  # Pre-tokenize

    print(f"\nInput: {text2}")
    print("Pre-tokenized with custom tokenization")

    # Check spelling (will use existing tokens)
    cas2, result2 = checker.check_cas(cas2)

    print(f"Errors found: {result2['error_count']}\n")

    for error in result2["errors"]:
        print(f"  '{error['word']}' -> {error['suggestions'][0]}")

    print("\n" + "=" * 70)
    print("Example 3: Compare with traditional Text API")
    print("=" * 70)

    text3 = "This is a tset"

    # Traditional API
    result_text = checker.check_text(text3)
    print(f"\nTraditional API:")
    print(f"  Text: {text3}")
    print(f"  Errors: {result_text['error_count']}")

    # CAS API
    cas3 = create_cas(text3)
    cas3, result_cas = checker.check_cas(cas3)
    print(f"\nCAS API:")
    print(f"  Text: {text3}")
    print(f"  Errors: {result_cas['error_count']}")

    print("\nBoth APIs produce equivalent results!")

    print("\n" + "=" * 70)
    print("Benefits of CAS API:")
    print("=" * 70)
    print("""
    1. Standard format: CAS is a standard from UIMA/DKPro
    2. Rich annotations: Store multiple annotation layers
    3. Interoperability: Works with other NLP tools
    4. Flexibility: Use your own tokenization or let LeSpell tokenize
    5. Handoff: Error detection and correction communicate via CAS
    """)


if __name__ == "__main__":
    main()
