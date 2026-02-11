# LeSpell

A Python library for spelling error detection and analysis in learner corpora.

## Features

- **Data Preparation**: Convert multiple learner corpus formats (CITA, LitKey, TOEFL, MERLIN) to standardized format
- **Error Analysis**: Analyze spelling patterns and error types across corpora
- **LanguageTool Integration**: Detect and correct spelling and grammar errors
- **Extensible Architecture**: Abstract base classes for adding custom corpus converters
- **Type-Safe**: Full type hints with mypy support
- **Well-Tested**: 35+ comprehensive tests with CI/CD pipeline

## Installation

### Core Package

```bash
pip install lespell
```

### With Corpus Resources (optional)

To use data preparation converters, install the appropriate data packages:

```bash
# Install Italian CITA corpus support
pip install lespell-data-cita

# Install English LitKey corpus support
pip install lespell-data-litkey

# Install TOEFL corpus support
pip install lespell-data-toefl

# Install all language models and dictionaries
pip install lespell-data-languagemodels
pip install lespell-data-dictionaries
```

For development, resources are available in the `data/` directory at the repository root.

## Quick Start

### Basic Usage

```python
from lespell.io import SpellingItem, SpellingReader, SpellingWriter

# Read spelling error data
reader = SpellingReader()
items = reader.read("path/to/corpus.xml")

# Process items...

# Write results to CSV/TSV
writer = SpellingWriter()
writer.write_csv(items, "output.csv")
writer.write_tsv(items, "output.tsv")
```

### Converting Learner Corpora

```python
from lespell.data_prep import CitaConverter, LitkeyConverter, ToeflConverter

# Convert CITA corpus (Italian)
cita = CitaConverter()
items = cita.convert("path/to/cita/corpus")

# Convert LitKey corpus (English)
litkey = LitkeyConverter()
items = litkey.convert("path/to/litkey/corpus")

# Convert TOEFL corpus (English)
toefl = ToeflConverter()
items = toefl.convert("path/to/toefl/corpus")
```

### Error Detection and Correction

```python
from lespell.integrations import LanguageToolDetector, LanguageToolCorrector

# Detect spelling errors
detector = LanguageToolDetector(language="en")
errors = detector.detect_errors("This is a tst.")

# Correct text
corrector = LanguageToolCorrector(language="en")
corrected = corrector.correct_text("This is a tst.")
print(corrected)  # "This is a test."
```

### Error Analysis

```python
from lespell.analysis import SpellingAnalyzer

# Analyze error patterns
analyzer = SpellingAnalyzer()
stats = analyzer.analyze(items)
print(f"Total errors: {stats['total_errors']}")
print(f"Unique errors: {stats['unique_errors']}")
```

## Project Structure

```
lespell/
├── lespell/                 # Main package
│   ├── core.py             # SpellingItem data model
│   ├── reader.py           # XML corpus reader
│   ├── writer.py           # CSV/TSV export writer
│   ├── data_prep/          # Corpus converters
│   │   ├── base.py         # BaseConverter abstract class
│   │   ├── cita.py         # CITA Italian corpus converter
│   │   ├── litkey.py       # LitKey English corpus converter
│   │   └── toefl.py        # TOEFL corpus converter
│   ├── analysis/           # Error analysis utilities
│   │   └── average_levenshtein.py
│   └── languagetool/       # LanguageTool integration
│
├── data/                    # External resources (not in pip package)
│   ├── corpora/            # Learner corpora
│   ├── dictionaries/       # Spelling dictionaries
│   ├── language_models/    # Frequency models
│   └── resources/          # G2P mappings, keyboards, descriptors
│
├── tests/                  # Test suite
├── pyproject.toml          # Poetry configuration
└── README.md               # This file
```

## Resource Organization

The library uses **external resources** to keep the core package lightweight:

- **Core Package** (~100 KB): Code only, no resource files
- **Data Packages**: Separate installable packages for each corpus/resource type

See [data/README.md](data/README.md) for detailed resource documentation.

## Development

### Setup

```bash
# Install development environment
poetry install --with dev

# Activate virtual environment  
poetry shell
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=lespell

# Run specific test file
pytest tests/test_core.py -v
```

### Code Quality

```bash
# Format code
black lespell tests

# Sort imports
isort lespell tests

# Lint
ruff check lespell tests

# Type checking
mypy lespell
```

## API Documentation

### Core Classes

#### SpellingItem
Represents a single spelling error with correction information.

#### SpellingReader
Reads spelling error data from XML files.

#### SpellingWriter
Writes spelling items to CSV or TSV format.

### Converters

All converters inherit from `BaseConverter` and implement:
- `convert(source_path)`: Transform corpus to SpellingItem list
- `get_corpus_name()`: Return corpus name

### Analysis

Utilities for statistical analysis of error patterns:
- Levenshtein distance calculations
- Error type distributions
- Corpus statistics

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Citation

If you use LeSpell in your research, please cite:

```bibtex
@software{lespell2024,
  title={LeSpell: A Python Library for Spelling Error Detection and Analysis},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/lespell}
}
```

## Acknowledgments

This library builds upon the original Java spelling analysis project. The port to Python includes modern packaging, comprehensive testing, and modular resource organization.