"""Simple dict-based annotation and pipeline system."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


@dataclass
class Annotation:
    """Represents an annotation on text span."""

    type: str
    start: int
    end: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"{self.type}({self.start}-{self.end})"


@dataclass
class Text:
    """Represents text with annotations."""

    content: str
    annotations: List[Annotation] = field(default_factory=list)

    def get_annotations_by_type(self, annotation_type: str) -> List[Annotation]:
        """Get all annotations of a specific type."""
        return [a for a in self.annotations if a.type == annotation_type]

    def add_annotation(self, annotation: Annotation) -> None:
        """Add an annotation."""
        self.annotations.append(annotation)

    def get_span_text(self, start: int, end: int) -> str:
        """Get text for a span."""
        return self.content[start:end]

    def get_overlapping_annotations(self, start: int, end: int) -> List[Annotation]:
        """Get annotations that overlap a span."""
        return [
            a for a in self.annotations if not (a.end <= start or a.start >= end)
        ]

    def get_tokens(self) -> List[tuple]:
        """Extract tokens from text (simple whitespace-based).

        Returns:
            List of (start, end, text) tuples
        """
        tokens = []
        start = 0
        for i, char in enumerate(self.content + " "):
            if char.isspace():
                if i > start:
                    text = self.content[start:i]
                    tokens.append((start, i, text))
                start = i + 1
        return tokens


class Pipeline:
    """Annotation pipeline that processes text through multiple stages."""

    def __init__(self, name: str = "pipeline"):
        self.name = name
        self.stages: List[tuple] = []  # (stage_name, function)

    def add_stage(self, name: str, processor: Callable[[Text], Text]) -> "Pipeline":
        """Add a processing stage to the pipeline."""
        self.stages.append((name, processor))
        return self

    def process(self, text: Text) -> Text:
        """Process text through all pipeline stages."""
        result = text
        for _, processor in self.stages:
            result = processor(result)
        return result
