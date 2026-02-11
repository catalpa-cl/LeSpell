"""Base converter class and utilities for corpus converters.

Resource Location:
    Converter implementations reference corpus files from external sources.
    For development, resources are stored in the data/ directory at repository root.
    For production, install separate data packages (lespell-data-cita, lespell-data-litkey, etc.)
    that register resource paths with the library.

Example:
    >>> from lespell.data_prep import CitaConverter
    >>> converter = CitaConverter()
    >>> items = converter.convert("path/to/corpus/directory")
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Union

from lespell.io import SpellingItem


class BaseConverter(ABC):
    """Abstract base class for corpus converters.
    
    Converters transform various learner corpus formats into standardized
    SpellingItem objects. Each converter handles a specific corpus format
    and expects input data in the appropriate structure.
    """

    @abstractmethod
    def convert(self, source_path: Union[str, Path]) -> List[SpellingItem]:
        """Convert source corpus to SpellingItem list.

        Args:
            source_path: Path to source corpus directory or file

        Returns:
            List of SpellingItem objects
        """
        pass

    @abstractmethod
    def get_corpus_name(self) -> str:
        """Return the name of this corpus.

        Returns:
            Corpus name string
        """
        pass
