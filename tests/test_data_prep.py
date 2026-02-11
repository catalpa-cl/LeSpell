"""Tests for data preparation converters."""

import tempfile
from pathlib import Path

import pytest

from lespell.data_prep import CitaConverter, LitkeyConverter, ToeflConverter


@pytest.fixture
def temp_cita_corpus():
    """Create a temporary CITA-like corpus."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create I-year folder
        i_year = tmpdir / "I-year"
        i_year.mkdir()

        # Create a sample CITA file - note: using proper XML structure
        cita_content = """<data>This is a <M t="20" c="test">tst</M> text with <M t="99" c="an">a</M> error.</data>"""

        with open(i_year / "test_001.txt", "w", encoding="utf-8") as f:
            f.write(cita_content)

        yield tmpdir


class TestCitaConverter:
    """Test CITA corpus converter."""

    def test_converter_name(self):
        """Test converter returns correct corpus name."""
        converter = CitaConverter()
        assert converter.get_corpus_name() == "CItA"

    def test_convert_cita_corpus(self, temp_cita_corpus):
        """Test converting a CITA corpus."""
        converter = CitaConverter()
        items = converter.convert(temp_cita_corpus)

        assert len(items) > 0, f"Expected items but got {len(items)}"
        assert items[0].corpus_name == "CItA"

    def test_cita_error_extraction(self, temp_cita_corpus):
        """Test that CITA converter extracts errors correctly."""
        converter = CitaConverter()
        items = converter.convert(temp_cita_corpus)

        assert len(items) > 0, f"Expected items but got {len(items)}"
        item = items[0]

        # Should have spelling and grammar errors
        assert item.num_spelling_errors > 0 or item.num_grammar_errors > 0


class TestLitkeyConverter:
    """Test LitKey corpus converter."""

    def test_converter_name(self):
        """Test converter returns correct corpus name."""
        converter = LitkeyConverter()
        assert converter.get_corpus_name() == "LitKey"


class TestToeflConverter:
    """Test TOEFL corpus converter."""

    def test_converter_name(self):
        """Test converter returns correct corpus name."""
        converter = ToeflConverter()
        assert converter.get_corpus_name() == "TOEFL"
