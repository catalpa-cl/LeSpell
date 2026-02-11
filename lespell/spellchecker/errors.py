"""Spelling error representation and utilities."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from lespell.spellchecker.annotations import Annotation


@dataclass
class SpellingError:
    """Represents a detected spelling error."""

    start: int
    end: int
    word: str
    error_type: str = "spelling_error"
    context: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"SpellingError({self.start}-{self.end}: '{self.word}')"

    @classmethod
    def from_annotation(
        cls,
        annotation: Annotation,
        text_content: str,
        context: Optional[str] = None,
    ) -> "SpellingError":
        """Create SpellingError from Annotation.

        Args:
            annotation: Annotation object with start, end, type
            text_content: Full text content to extract word
            context: Optional context string

        Returns:
            SpellingError instance
        """
        word = text_content[annotation.start : annotation.end]
        return cls(
            start=annotation.start,
            end=annotation.end,
            word=word,
            error_type=annotation.type,
            context=context,
            metadata=annotation.metadata.copy() if annotation.metadata else {},
        )
