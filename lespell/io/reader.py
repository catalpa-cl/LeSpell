"""Reader for parsing spelling error XML files."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Union

from lespell.io.core import SpellingItem


class SpellingReader:
    """Reads spelling error XML files and produces SpellingItem objects.

    The XML format expected is:
        <corpus name="corpus_name">
            <spelling_text id="text_id" lang="language_code">
                Text with <error correct="correction" type="error_type">
                misspelling</error> and
                <grammar_error correct="correction">grammar issue</grammar_error>.
            </spelling_text>
        </corpus>
    """

    def __init__(
        self, source_file: Union[str, Path], language: str, encoding: str = "utf-8"
    ):
        """Initialize the reader.

        Args:
            source_file: Path to the XML file to read
            language: Language code to filter texts (e.g., 'en', 'de', 'it')
            encoding: Text encoding (default: utf-8)
        """
        self.source_file = Path(source_file)
        self.language = language
        self.encoding = encoding
        self.items: List[SpellingItem] = []
        self._read_file()

    def _read_file(self) -> None:
        """Parse the XML file and populate items list."""
        tree = ET.parse(self.source_file)
        root = tree.getroot()
        corpus_name = root.get("name", "unknown")

        for text_elem in root.findall("spelling_text"):
            text_id = text_elem.get("id", "")
            lang = text_elem.get("lang", "")

            # Workaround for missing lang attribute (e.g., in Merlin corpus)
            if not lang:
                if text_id.startswith("german"):
                    lang = "de"
                elif text_id.startswith("italian"):
                    lang = "it"
                elif text_id.startswith("czech"):
                    lang = "cz"

            # Only read texts in the requested language
            if lang != self.language:
                continue

            # Extract text with error markup
            text, corrections, error_types, grammar_corrections = self._parse_text_element(
                text_elem
            )

            item = SpellingItem(
                corpus_name=corpus_name,
                text_id=text_id,
                text=text,
                corrections=corrections,
                correction_error_types=error_types,
                grammar_corrections=grammar_corrections,
            )
            self.items.append(item)

        print(f"Reader: Loaded {len(self.items)} texts in language '{self.language}'")

    def _parse_text_element(self, text_elem: ET.Element) -> tuple:
        """Parse a spelling_text element and extract text and error information.

        Returns:
            Tuple of (text, corrections_dict, error_types_dict, grammar_corrections_dict)
        """
        text_parts = []
        corrections = {}
        error_types = {}
        grammar_corrections = {}
        current_pos = 0

        # Process text and error elements
        if text_elem.text:
            text_parts.append(text_elem.text)
            current_pos += len(text_elem.text)

        for child in text_elem:
            if child.tag == "error":
                misspelling = child.text or ""
                correction = child.get("correct", "")
                error_type = child.get("type", "")

                span = f"{current_pos}-{current_pos + len(misspelling)}"
                corrections[span] = correction
                error_types[span] = error_type

                text_parts.append(misspelling)
                current_pos += len(misspelling)

            elif child.tag == "grammar_error":
                misspelling = child.text or ""
                correction = child.get("correct", "")

                span = f"{current_pos}-{current_pos + len(misspelling)}"
                grammar_corrections[span] = correction

                text_parts.append(misspelling)
                current_pos += len(misspelling)

            else:
                # Unknown tag, skip it
                pass

            # Add tail text (text after the element)
            if child.tail:
                text_parts.append(child.tail)
                current_pos += len(child.tail)

        return "".join(text_parts), corrections, error_types, grammar_corrections

    def get_items(self) -> List[SpellingItem]:
        """Return list of all loaded spelling items."""
        return self.items

    def __iter__(self):
        """Allow iteration over items."""
        return iter(self.items)

    def __len__(self) -> int:
        """Return number of items loaded."""
        return len(self.items)
