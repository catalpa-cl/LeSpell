#!/usr/bin/env python3
"""Batch spell checking example with SpellingItem."""

from lespell.integrations import HunspellWrapper
from lespell.io import SpellingItem
from lespell.spellchecker import (
    CostBasedRanker,
    DictionaryErrorDetector,
    HunspellCandidateGenerator,
    LevenshteinCandidateGenerator,
    SpellingChecker,
)


def main():
    """Process multiple spelling items in batch."""
    dictionary = {
        "the", "student", "received", "a", "good", "grade",
        "she", "has", "excellent", "writing", "skills",
        "they", "were", "happy", "with", "results",
    }

    detector = DictionaryErrorDetector(dictionary=dictionary)

    # Initialize Hunspell wrapper
    hunspell = HunspellWrapper(language="en")

    checker = SpellingChecker(
        detector=detector,
        candidate_generators=[
            LevenshteinCandidateGenerator(
                language="en",
                dictionary=dictionary,
                max_candidates=10,
            ),
            HunspellCandidateGenerator(hunspell),
        ],
        ranker=CostBasedRanker(),
    )

    items = [
        SpellingItem(
            corpus_name="learner",
            text_id="001",
            text="The student recieved a good grade.",
            corrections={"12-20": "received"},
        ),
        SpellingItem(
            corpus_name="learner",
            text_id="002",
            text="She has excellant writing skills.",
            corrections={"9-18": "excellent"},
        ),
        SpellingItem(
            corpus_name="learner",
            text_id="003",
            text="They where happy with the resulst.",
            corrections={"5-10": "were", "30-37": "results"},
        ),
    ]

    results = checker.check_spelling_items(items)

    for result in results:
        print(f"[{result['text_id']}] {result['text']}")
        print(f"  Errors: {result['error_count']}, Corrections: {result['gold_corrections']}")
        if result["errors"]:
            for error in result["errors"]:
                print(f"    '{error['word']}' → {error['suggestions'][:2]}")
        print()


if __name__ == "__main__":
    main()
