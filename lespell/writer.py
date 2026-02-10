"""Writer for exporting spelling items to various formats."""

import csv
from pathlib import Path
from typing import List, Union

from lespell.core import SpellingItem


class SpellingWriter:
    """Exports SpellingItem objects to various formats."""

    @staticmethod
    def to_tsv(
        items: List[SpellingItem],
        output_file: Union[str, Path],
        include_grammar: bool = True,
    ) -> None:
        """Write spelling items to TSV format.

        Args:
            items: List of SpellingItem objects
            output_file: Path to output TSV file
            include_grammar: Include grammar errors in output
        """
        output_file = Path(output_file)

        with open(output_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter="\t")

            # Write header
            writer.writerow(["corpus", "text_id", "text", "error_span", "correction", "type"])

            for item in items:
                # Write spelling errors
                for span, correction in item.corrections.items():
                    error_type = item.get_error_type(span) or "spelling"
                    writer.writerow(
                        [
                            item.corpus_name,
                            item.text_id,
                            item.text,
                            span,
                            correction,
                            error_type,
                        ]
                    )

                # Write grammar errors if requested
                if include_grammar:
                    for span, correction in item.grammar_corrections.items():
                        writer.writerow(
                            [
                                item.corpus_name,
                                item.text_id,
                                item.text,
                                span,
                                correction,
                                "grammar",
                            ]
                        )

    @staticmethod
    def to_csv(
        items: List[SpellingItem],
        output_file: Union[str, Path],
        include_grammar: bool = True,
    ) -> None:
        """Write spelling items to CSV format.

        Args:
            items: List of SpellingItem objects
            output_file: Path to output CSV file
            include_grammar: Include grammar errors in output
        """
        output_file = Path(output_file)

        with open(output_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(["corpus", "text_id", "text", "error_span", "correction", "type"])

            for item in items:
                # Write spelling errors
                for span, correction in item.corrections.items():
                    error_type = item.get_error_type(span) or "spelling"
                    writer.writerow(
                        [
                            item.corpus_name,
                            item.text_id,
                            item.text,
                            span,
                            correction,
                            error_type,
                        ]
                    )

                # Write grammar errors if requested
                if include_grammar:
                    for span, correction in item.grammar_corrections.items():
                        writer.writerow(
                            [
                                item.corpus_name,
                                item.text_id,
                                item.text,
                                span,
                                correction,
                                "grammar",
                            ]
                        )
