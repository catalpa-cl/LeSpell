"""TOEFL corpus converter - transforms TOEFL learner corpus to standard format.

The TOEFL corpus contains sentences with aligned corrections.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Union

from lespell.io import SpellingItem
from lespell.data_prep.base import BaseConverter


class ToeflConverter(BaseConverter):
    """Converter for TOEFL learner corpus."""

    def convert(self, source_path: Union[str, Path]) -> List[SpellingItem]:
        """Convert TOEFL corpus to SpellingItem list.

        Args:
            source_path: Path to TOEFL corpus directory or file

        Returns:
            List of SpellingItem objects
        """
        source_path = Path(source_path)
        items = []

        if source_path.is_file() and source_path.suffix == ".xml":
            # Single file
            items.extend(self._process_file(source_path))
        else:
            # Directory - process all XML files
            for file_path in sorted(source_path.glob("**/*.xml")):
                items.extend(self._process_file(file_path))

        return items

    def _process_file(self, file_path: Path) -> List[SpellingItem]:
        """Process a single TOEFL corpus file.

        Args:
            file_path: Path to XML file

        Returns:
            List of SpellingItem objects from this file
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError:
            return []

        items = []

        # TOEFL structure: each <essay> is a text
        for essay_elem in root.findall(".//essay"):
            text_id = essay_elem.get("id", "unknown")
            text, corrections, error_types = self._extract_errors_from_essay(essay_elem)

            if text:
                item = SpellingItem(
                    corpus_name=self.get_corpus_name(),
                    text_id=text_id,
                    text=text,
                    corrections=corrections,
                    correction_error_types=error_types,
                )
                items.append(item)

        return items

    def _extract_errors_from_essay(self, essay_elem: ET.Element) -> tuple:
        """Extract text and errors from an essay element.

        Returns:
            Tuple of (text, corrections_dict, error_types_dict)
        """
        text_parts = []
        corrections = {}
        error_types = {}
        current_pos = 0

        # Process paragraphs
        for para_elem in essay_elem.findall(".//paragraph"):
            for sent_elem in para_elem.findall(".//sentence"):
                text_content = sent_elem.text or ""
                text_parts.append(text_content)

                # Extract error annotations from sentence
                for error_elem in sent_elem.findall(".//error"):
                    start = int(error_elem.get("start", 0))
                    end = int(error_elem.get("end", 0))
                    correction = error_elem.get("correction", "")
                    error_type = error_elem.get("type", "spelling")

                    # Adjust positions based on current text position
                    adjusted_start = current_pos + start
                    adjusted_end = current_pos + end
                    span = f"{adjusted_start}-{adjusted_end}"

                    corrections[span] = correction
                    error_types[span] = error_type

                current_pos += len(text_content)

            # Add space between paragraphs if needed
            if current_pos > 0 and not text_parts[-1].endswith(" "):
                text_parts.append(" ")
                current_pos += 1

        return "".join(text_parts), corrections, error_types

    def get_corpus_name(self) -> str:
        """Return corpus name."""
        return "TOEFL"
