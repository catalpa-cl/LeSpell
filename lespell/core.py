"""Core data structures for LeSpell."""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class SpellingItem:
    """Represents a single spelling item from a corpus.

    Attributes:
        corpus_name: Name of the corpus this item comes from
        text_id: Unique identifier for this text
        text: The full text content
        corrections: Mapping of error spans (start-end) to corrections
        correction_error_types: Mapping of error spans to error types
        grammar_corrections: Mapping of grammar error spans to corrections
    """

    corpus_name: str
    text_id: str
    text: str
    corrections: Dict[str, str] = field(default_factory=dict)
    correction_error_types: Dict[str, str] = field(default_factory=dict)
    grammar_corrections: Dict[str, str] = field(default_factory=dict)

    @property
    def num_spelling_errors(self) -> int:
        """Return number of spelling errors."""
        return len(self.corrections)

    @property
    def num_grammar_errors(self) -> int:
        """Return number of grammar errors."""
        return len(self.grammar_corrections)

    def get_correction(self, span: str) -> Optional[str]:
        """Get correction for an error span (format: 'start-end')."""
        return self.corrections.get(span)

    def get_error_type(self, span: str) -> Optional[str]:
        """Get error type for a spelling error span."""
        return self.correction_error_types.get(span)

    def get_grammar_correction(self, span: str) -> Optional[str]:
        """Get correction for a grammar error span."""
        return self.grammar_corrections.get(span)
