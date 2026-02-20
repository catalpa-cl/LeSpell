#!/usr/bin/env python3
"""PySpellChecker integration example with LeSpell."""

from lespell.integrations import PyspellcheckerWrapper


def main():
    """Demonstrate spell checking using PySpellChecker integration."""
    # Create PySpellChecker wrapper
    wrapper = PyspellcheckerWrapper(language="en")

    # Example: Check individual words
    test_words = ["tset", "speling", "correct", "communication"]
    
    print("Word-level checking:")
    for word in test_words:
        is_correct = wrapper.check(word)
        if not is_correct:
            suggestions = wrapper.correct(word)
            print(f"  '{word}': suggestions = {suggestions[:3]}")
        else:
            print(f"  '{word}': correct")
    
    print()


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
