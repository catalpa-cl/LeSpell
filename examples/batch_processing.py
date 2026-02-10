#!/usr/bin/env python3
"""Example: Batch spell checking with SpellingItem."""

from lespell.spellchecker import (
    SpellingChecker,
    LevenshteinCandidateGenerator,
    HunspellCandidateGenerator,
    CostBasedRanker,
    SimplePreprocessor,
)
from lespell.core import SpellingItem


def create_simple_dictionary():
    """Create a simple dictionary for demonstration."""
    return {
        "the", "student", "received", "a", "good", "grade",
        "she", "has", "excellent", "writing", "skills",
        "they", "were", "happy", "with", "results",
    }


def main():
    """Process multiple spelling items."""
    print("=" * 60)
    print("LeSpell - Batch Processing Example")
    print("=" * 60)

    # Initialize spell checker with multiple generators
    print("\n1. Initializing multi-generator spell checker...")
    dictionary = create_simple_dictionary()
    
    checker = SpellingChecker(
        candidate_generators=[
            LevenshteinCandidateGenerator(
                language="en",
                dictionary=dictionary,
                substitution_weight=1.0,
                max_candidates=10,
            ),
            HunspellCandidateGenerator(),  # Dictionary-based
        ],
        ranker=CostBasedRanker(),
        preprocessor=SimplePreprocessor(),
    )
    print("   ✓ Spell checker ready with 2 generators")

    # Create sample spelling items (from a corpus)
    print("\n2. Creating sample corpus items...")
    items = [
        SpellingItem(
            corpus_name="learner_corpus",
            text_id="text_001",
            text="The student recieved a good grade.",
            corrections={"12-20": "received"},
        ),
        SpellingItem(
            corpus_name="learner_corpus",
            text_id="text_002",
            text="She has excellant writing skills.",
            corrections={"9-18": "excellent"},
        ),
        SpellingItem(
            corpus_name="learner_corpus",
            text_id="text_003",
            text="They where happy with the resulst.",
            corrections={"5-10": "were", "30-37": "results"},
        ),
    ]
    print(f"   ✓ Created {len(items)} corpus items")

    # Process all items
    print("\n3. Processing corpus items...")
    results = checker.check_spelling_items(items)

    # Display results
    print(f"\n4. Results for {len(results)} items:\n")
    for result in results:
        print(f"   Corpus: {result['corpus_name']}")
        print(f"   Text ID: {result['text_id']}")
        print(f"   Text: '{result['text']}'")
        print(f"   Found errors: {result['error_count']}")
        print(f"   Gold corrections: {result['gold_corrections']}")
        
        if result["errors"]:
            for error in result["errors"]:
                print(f"     • '{error['word']}' → {error['suggestions'][:3]}")
        print()

    # Summary
    print("=" * 60)
    total_errors = sum(r["error_count"] for r in results)
    print(f"✓ Summary: Found {total_errors} total errors across {len(results)} items")
    print("=" * 60)


if __name__ == "__main__":
    main()
