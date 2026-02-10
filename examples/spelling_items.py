#!/usr/bin/env python3
"""Example: Working with SpellingItem objects."""

from lespell.core import SpellingItem


def main():
    """Demonstrate SpellingItem usage."""
    print("=" * 60)
    print("LeSpell - SpellingItem Example")
    print("=" * 60)

    # Create a spelling item (from a learner corpus)
    print("\n1. Creating a SpellingItem...")
    item = SpellingItem(
        corpus_name="CITA",
        text_id="student_001",
        text="The student recieved a good grade.",
        corrections={"12-20": "received"},
        correction_error_types={"12-20": "spelling"},
    )
    print("   ✓ SpellingItem created")

    # Display item properties
    print("\n2. Item properties:")
    print(f"   Corpus: {item.corpus_name}")
    print(f"   Text ID: {item.text_id}")
    print(f"   Text: '{item.text}'")
    print(f"   Number of spelling errors: {item.num_spelling_errors}")

    # Access corrections
    print("\n3. Corrections:")
    for span, correction in item.corrections.items():
        start, end = map(int, span.split("-"))
        original = item.text[start:end]
        error_type = item.get_error_type(span)
        print(f"   Span {span}: '{original}' → '{correction}' (type: {error_type})")

    # Create multiple items
    print("\n4. Creating a batch of items...")
    items = [
        SpellingItem(
            corpus_name="CITA",
            text_id=f"student_{i:03d}",
            text=f"Text {i}: Example sentence with erors.",
            corrections={"24-29": "errors"},
        )
        for i in range(1, 4)
    ]
    print(f"   ✓ Created {len(items)} items")

    # Process batch
    print("\n5. Processing batch:")
    total_errors = sum(item.num_spelling_errors for item in items)
    total_texts = len(items)
    print(f"   Total texts: {total_texts}")
    print(f"   Total spelling errors: {total_errors}")
    print(f"   Average errors per text: {total_errors/total_texts:.2f}")

    # Grammar corrections example
    print("\n6. Grammar corrections example:")
    item_with_grammar = SpellingItem(
        corpus_name="CITA",
        text_id="student_004",
        text="She go to school every day.",
        corrections={"4-6": "goes"},  # Spelling/grammar error
        correction_error_types={"4-6": "agreement"},
    )
    print(f"   Text: '{item_with_grammar.text}'")
    print(f"   Grammar errors: {item_with_grammar.num_grammar_errors}")
    for span, correction in item_with_grammar.corrections.items():
        error_type = item_with_grammar.get_error_type(span)
        print(f"   • '{item_with_grammar.text}' → '{correction}' [{error_type}]")

    print("\n" + "=" * 60)
    print("✓ SpellingItem example complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
