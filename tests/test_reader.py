"""Tests for the SpellingReader."""

import pytest
from pathlib import Path

from lespell.io import SpellingReader


@pytest.fixture
def test_xml_path():
    """Return path to test XML file."""
    return Path(__file__).parent / "fixtures" / "test_corpus.xml"


def test_reader_load_items(test_xml_path):
    """Test that reader loads items correctly."""
    reader = SpellingReader(test_xml_path, language="en")
    items = reader.get_items()

    assert len(items) == 2
    assert items[0].text_id == "test_001"
    assert items[1].text_id == "test_002"


def test_reader_corpus_name(test_xml_path):
    """Test that corpus name is extracted correctly."""
    reader = SpellingReader(test_xml_path, language="en")
    items = reader.get_items()

    assert all(item.corpus_name == "test_corpus" for item in items)


def test_reader_language_filtering(test_xml_path):
    """Test that reader filters by language."""
    reader_en = SpellingReader(test_xml_path, language="en")
    reader_de = SpellingReader(test_xml_path, language="de")

    assert len(reader_en.get_items()) == 2
    assert len(reader_de.get_items()) == 1
    assert reader_de.get_items()[0].text_id == "test_003"


def test_reader_spelling_errors(test_xml_path):
    """Test that spelling errors are extracted correctly."""
    reader = SpellingReader(test_xml_path, language="en")
    item = reader.get_items()[0]

    assert item.num_spelling_errors == 1
    assert "8-11" in item.corrections
    assert item.get_correction("8-11") == "a"
    assert item.get_error_type("8-11") == "article"


def test_reader_grammar_errors(test_xml_path):
    """Test that grammar errors are extracted correctly."""
    reader = SpellingReader(test_xml_path, language="en")
    item = reader.get_items()[0]

    assert item.num_grammar_errors == 1
    assert "27-28" in item.grammar_corrections
    assert item.get_grammar_correction("27-28") == "an"


def test_reader_text_content(test_xml_path):
    """Test that text content is reconstructed correctly."""
    reader = SpellingReader(test_xml_path, language="en")
    item = reader.get_items()[0]

    # The text should have errors reconstructed
    assert "This is" in item.text
    assert "the" in item.text  # misspelling
    assert "test text" in item.text


def test_reader_iteration(test_xml_path):
    """Test iteration over reader items."""
    reader = SpellingReader(test_xml_path, language="en")
    
    count = 0
    for item in reader:
        count += 1
        assert hasattr(item, "text")
        assert hasattr(item, "text_id")

    assert count == 2


def test_reader_length(test_xml_path):
    """Test len() on reader."""
    reader = SpellingReader(test_xml_path, language="en")
    assert len(reader) == 2
