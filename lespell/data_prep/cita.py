"""CITA corpus converter - transforms CItA Italian learner corpus to standard format.

The CItA corpus marks errors with <M> elements:
    <M t="20" c="compiti">conpiti</M>
    
Where t is error type (20-25 are spelling, others are grammar).
Type mapping:
    20-25: Spelling errors -> <error>
    Others: Grammar/other errors -> <grammar_error>
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Union

from lespell.core import SpellingItem
from lespell.data_prep.base import BaseConverter


class CitaConverter(BaseConverter):
    """Converter for CITA Italian learner corpus."""

    SPELLING_ERROR_TYPES = {"20", "21", "22", "23", "24", "25"}

    def convert(self, source_path: Union[str, Path]) -> List[SpellingItem]:
        """Convert CITA corpus to SpellingItem list.

        Args:
            source_path: Path to CItA corpus directory
                Expected structure: source_path/I-year/ and source_path/II-year/

        Returns:
            List of SpellingItem objects
        """
        source_path = Path(source_path)
        items = []

        # Process both year folders
        for year_folder in ["I-year", "II-year"]:
            year_path = source_path / year_folder
            if not year_path.exists():
                continue

            for file_path in sorted(year_path.glob("*.txt")):
                items.extend(self._process_file(file_path, year_folder))

        return items

    def _process_file(self, file_path: Path, year_folder: str) -> List[SpellingItem]:
        """Process a single CITA corpus file.

        Args:
            file_path: Path to text file
            year_folder: Name of year folder (for text ID)

        Returns:
            List of SpellingItem objects from this file
        """
        with open(file_path, "r", encoding="utf-8") as f:
            text_content = f.read()

        # Escape special XML characters
        text_content = text_content.replace("&", "&amp;")
        text_content = text_content.replace("<<", "&lt;&lt;")

        # Wrap in root element for XML parsing if not already wrapped
        if not text_content.strip().startswith("<"):
            text_content = f"<data>{text_content}</data>"

        try:
            root = ET.fromstring(text_content)
        except ET.ParseError:
            # If parsing fails, return empty list
            return []

        # Extract text ID from filename
        text_id = file_path.stem

        # Reconstruct text with error information
        text, corrections, error_types, grammar_corrections = self._extract_errors(root)

        if text:
            item = SpellingItem(
                corpus_name=self.get_corpus_name(),
                text_id=f"{year_folder}_{text_id}",
                text=text,
                corrections=corrections,
                correction_error_types=error_types,
                grammar_corrections=grammar_corrections,
            )
            return [item]

        return []

    def _extract_errors(self, root: ET.Element) -> tuple:
        """Extract text and error information from XML root.

        Returns:
            Tuple of (text, corrections_dict, error_types_dict, grammar_corrections_dict)
        """
        text_parts = []
        corrections = {}
        error_types = {}
        grammar_corrections = {}
        current_pos = 0

        # Process text and M (markup) elements
        if root.text:
            text_parts.append(root.text)
            current_pos += len(root.text)

        for child in root:
            if child.tag == "M":
                # Extract error information
                misspelled = child.text or ""
                correction = child.get("c", "")  # correct attribute
                error_type = child.get("t", "")  # type attribute

                span = f"{current_pos}-{current_pos + len(misspelled)}"

                if error_type in self.SPELLING_ERROR_TYPES:
                    corrections[span] = correction
                    error_types[span] = error_type
                else:
                    grammar_corrections[span] = correction

                text_parts.append(misspelled)
                current_pos += len(misspelled)

            # Add tail text
            if child.tail:
                text_parts.append(child.tail)
                current_pos += len(child.tail)

        return "".join(text_parts), corrections, error_types, grammar_corrections

    def get_corpus_name(self) -> str:
        """Return corpus name."""
        return "CItA"
