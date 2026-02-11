"""Tests for core data structures."""


from lespell.io import SpellingItem


def test_spelling_item_basic():
    """Test basic SpellingItem creation."""
    item = SpellingItem(
        corpus_name="test_corpus",
        text_id="test_001",
        text="This is a test text",
    )
    assert item.corpus_name == "test_corpus"
    assert item.text_id == "test_001"
    assert item.text == "This is a test text"
    assert item.num_spelling_errors == 0
    assert item.num_grammar_errors == 0


def test_spelling_item_with_corrections():
    """Test SpellingItem with spelling corrections."""
    corrections = {"0-5": "Those"}
    error_types = {"0-5": "spelling"}

    item = SpellingItem(
        corpus_name="test_corpus",
        text_id="test_001",
        text="This is a test",
        corrections=corrections,
        correction_error_types=error_types,
    )

    assert item.num_spelling_errors == 1
    assert item.get_correction("0-5") == "Those"
    assert item.get_error_type("0-5") == "spelling"


def test_spelling_item_with_grammar_corrections():
    """Test SpellingItem with grammar corrections."""
    grammar_corrections = {"8-10": "an"}

    item = SpellingItem(
        corpus_name="test_corpus",
        text_id="test_001",
        text="This is a test",
        grammar_corrections=grammar_corrections,
    )

    assert item.num_grammar_errors == 1
    assert item.get_grammar_correction("8-10") == "an"


def test_spelling_item_missing_correction():
    """Test getting non-existent correction."""
    item = SpellingItem(
        corpus_name="test_corpus",
        text_id="test_001",
        text="This is a test",
    )

    assert item.get_correction("0-5") is None
    assert item.get_error_type("0-5") is None
    assert item.get_grammar_correction("0-5") is None
