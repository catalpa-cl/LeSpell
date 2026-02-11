#!/usr/bin/env python3
"""Working with SpellingItem objects."""

from lespell.io import SpellingItem


def main():
    """Demonstrate SpellingItem usage."""
    # Single item
    item = SpellingItem(
        corpus_name="CITA",
        text_id="student_001",
        text="The student recieved a good grade.",
        corrections={"12-20": "received"},
        correction_error_types={"12-20": "spelling"},
    )

    print(f"Corpus: {item.corpus_name}")
    print(f"Text: {item.text}")
    print(f"Spelling errors: {item.num_spelling_errors}\n")

    for span, correction in item.corrections.items():
        start, end = map(int, span.split("-"))
        original = item.text[start:end]
        error_type = item.get_error_type(span)
        print(f"{span}: '{original}' → '{correction}' [{error_type}]")

    # Batch of items
    print("\n--- Batch Example ---")
    items = [
        SpellingItem(
            corpus_name="CITA",
            text_id=f"student_{i:03d}",
            text=f"Text {i}: Example sentence with erors.",
            corrections={"24-29": "errors"},
        )
        for i in range(1, 4)
    ]

    total_errors = sum(item.num_spelling_errors for item in items)
    print(f"Items: {len(items)}, Total errors: {total_errors}")
    print(f"Average errors/text: {total_errors/len(items):.2f}")


if __name__ == "__main__":
    main()
