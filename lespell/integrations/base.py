"""Base class for spell checker integrations."""

from abc import ABC, abstractmethod


class SpellingCheckerBase(ABC):
    """Base class defining the unified interface for spell checker integrations."""

    @abstractmethod
    def check(self, word: str) -> bool:
        """Check if a word is correctly spelled.

        Args:
            word: Word to check

        Returns:
            True if word is correct, False otherwise
        """
        pass

    @abstractmethod
    def correct(self, word: str) -> str:
        """Get the best correction for a misspelled word.

        Args:
            word: Word to correct

        Returns:
            Best correction suggestion, or the original word if no suggestions
        """
        pass

    @abstractmethod
    def correct_text(self, text: str) -> str:
        """Correct a full text by fixing spelling errors.

        Args:
            text: Text to correct

        Returns:
            Corrected text
        """
        pass
