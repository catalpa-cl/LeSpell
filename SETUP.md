# Development setup guide for LeSpell

## Prerequisites

- Python 3.9 or higher
- Poetry (for dependency management)

## Installation

### Using Poetry (Recommended)

```bash
# Install poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install the project and development dependencies
poetry install --with dev

# Activate the virtual environment
poetry shell
```

### Using pip

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in editable mode with development dependencies
pip install -e ".[dev]"
```

## Building the Package

```bash
# Using Poetry
poetry build

# Using pip/build
pip install build
python -m build
```

This will create distribution packages in the `dist/` directory:
- `dist/lespell-0.1.0.tar.gz` (source distribution)
- `dist/lespell-0.1.0-py3-none-any.whl` (wheel distribution)

## Testing

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_module.py

# Run with verbose output
pytest -v
```

## Code Quality

```bash
# Format code with black
black lespell tests

# Sort imports with isort
isort lespell tests

# Lint with ruff
ruff check lespell tests

# Type checking with mypy
mypy lespell
```

## Publishing

```bash
# Build the package
poetry build

# Publish to PyPI (requires credentials)
poetry publish

# Or manually:
pip install twine
twine upload dist/*
```

### Before publishing:
1. Update the version in `pyproject.toml`
2. Update the `__version__` in `lespell/__init__.py`
3. Add entries to CHANGELOG.md
4. Create a git tag: `git tag v0.1.0`

## Package Structure

```
lespell/
├── lespell/                    # Main package
│   ├── __init__.py
│   ├── data_prep/             # Data preparation utilities
│   │   ├── __init__.py
│   │   ├── convert_cita.py
│   │   ├── convert_litkey.py
│   │   └── convert_toefl.py
│   ├── analysis/              # Analysis tools
│   │   ├── __init__.py
│   │   └── average_levenshtein.py
│   └── languagetool/          # LanguageTool integration
│       ├── __init__.py
│       ├── languagetool_detection.py
│       └── languagetool_correction.py
├── tests/                     # Test suite
├── pyproject.toml            # Project metadata and dependencies
├── MANIFEST.in               # Distribution manifest
├── README.md                 # Project README
└── LICENSE                   # License file
```

## Next Steps

1. Update author information in `pyproject.toml` and `lespell/__init__.py`
2. Update project URLs with your GitHub repository
3. Add comprehensive tests in the `tests/` directory
4. Update the README.md with usage examples
5. Create a CHANGELOG.md to track versions
6. Set up CI/CD with GitHub Actions or similar
