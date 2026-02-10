"""Tests for the SpellingWriter."""

import csv
import tempfile
from pathlib import Path

import pytest

from lespell.core import SpellingItem
from lespell.writer import SpellingWriter


@pytest.fixture
def sample_items():
    """Create sample spelling items for testing."""
    return [
        SpellingItem(
            corpus_name="test_corpus",
            text_id="001",
            text="This is a tst.",
            corrections={"10-13": "test"},
            correction_error_types={"10-13": "spelling"},
            grammar_corrections={"0-4": "That"},
        ),
        SpellingItem(
            corpus_name="test_corpus",
            text_id="002",
            text="Anohter example.",
            corrections={"0-7": "Another"},
            correction_error_types={"0-7": "spelling"},
        ),
    ]


class TestSpellingWriter:
    """Test SpellingWriter functionality."""

    def test_writer_to_tsv(self, sample_items):
        """Test writing to TSV format."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".tsv") as f:
            tsv_file = f.name

        try:
            SpellingWriter.to_tsv(sample_items, tsv_file, include_grammar=True)

            # Read and verify
            with open(tsv_file, "r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter="\t")
                rows = list(reader)

            # Check header
            assert rows[0] == ["corpus", "text_id", "text", "error_span", "correction", "type"]

            # Check we have entries for spelling and grammar errors
            assert len(rows) > 1

            # Verify some content
            corpus_values = [row[0] for row in rows[1:]]
            assert all(v == "test_corpus" for v in corpus_values)
        finally:
            Path(tsv_file).unlink()

    def test_writer_to_csv(self, sample_items):
        """Test writing to CSV format."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
            csv_file = f.name

        try:
            SpellingWriter.to_csv(sample_items, csv_file, include_grammar=False)

            # Read and verify
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)

            # Check header
            assert rows[0] == ["corpus", "text_id", "text", "error_span", "correction", "type"]

            # Should not include grammar errors
            types = [row[5] for row in rows[1:]]
            assert "grammar" not in types
            assert "spelling" in types
        finally:
            Path(csv_file).unlink()

    def test_writer_csv_with_grammar(self, sample_items):
        """Test CSV output includes grammar when requested."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
            csv_file = f.name

        try:
            SpellingWriter.to_csv(sample_items, csv_file, include_grammar=True)

            # Read and verify
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)

            types = [row[5] for row in rows[1:]]
            # Should include grammar errors
            assert "grammar" in types
        finally:
            Path(csv_file).unlink()

    def test_writer_handles_empty_list(self):
        """Test writer handles empty item list."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".tsv") as f:
            tsv_file = f.name

        try:
            SpellingWriter.to_tsv([], tsv_file)

            with open(tsv_file, "r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter="\t")
                rows = list(reader)

            # Should have at least header
            assert len(rows) >= 1
            assert rows[0] == ["corpus", "text_id", "text", "error_span", "correction", "type"]
        finally:
            Path(tsv_file).unlink()
