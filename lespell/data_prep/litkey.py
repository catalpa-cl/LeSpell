"""LitKey corpus converter - transforms LitKey corpus to standard format.

LitKey uses aligned token markup where corrections are marked with attributes.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Union

from lespell.core import SpellingItem
from lespell.data_prep.base import BaseConverter


class LitkeyConverter(BaseConverter):
    """Converter for LitKey English learner corpus."""

    def convert(self, source_path: Union[str, Path]) -> List[SpellingItem]:
        """Convert LitKey corpus to SpellingItem list.

        Args:
            source_path: Path to LitKey corpus directory

        Returns:
            List of SpellingItem objects
        """
        source_path = Path(source_path)
        items = []

        # Process all XML files
        for file_path in sorted(source_path.glob("**/*.xml")):
            items.extend(self._process_file(file_path))

        return items

    def _process_file(self, file_path: Path) -> List[SpellingItem]:
        """Process a single LitKey corpus file.

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
        text_id = file_path.stem

        # LitKey structure: each <doc> is a text
        for doc_elem in root.findall(".//doc"):
            text, corrections, error_types = self._extract_errors_from_doc(doc_elem)

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

    def _extract_errors_from_doc(self, doc_elem: ET.Element) -> tuple:
        """Extract text and errors from a document element.

        Returns:
            Tuple of (text, corrections_dict, error_types_dict)
        """
        text_parts = []
        corrections = {}
        error_types = {}
        current_pos = 0

        # Process all sentence elements
        for sent_elem in doc_elem.findall(".//sent"):
            for token_elem in sent_elem:
                token_text = token_elem.text or ""
                text_parts.append(token_text)

                # Check for correction attributes
                orig = token_elem.get("orig")
                corrected = token_elem.get("corrected")

                if orig and corrected:
                    span = f"{current_pos}-{current_pos + len(orig)}"
                    corrections[span] = corrected

                    # Infer error type from token attributes
                    error_type = token_elem.get("type", "spelling")
                    error_types[span] = error_type

                current_pos += len(token_text)

            # Add space after sentence if needed
            if sent_elem.tail:
                text_parts.append(sent_elem.tail)
                current_pos += len(sent_elem.tail)

        return "".join(text_parts), corrections, error_types

    def get_corpus_name(self) -> str:
        """Return corpus name."""
        return "LitKey"
