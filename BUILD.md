# Configuration for build backend
[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"

# Quick reference for building the package:
# poetry build          # Creates .tar.gz and .whl in dist/
# python -m build       # Alternative using build module
#
# For development:
# poetry install         # Install in editable mode with all deps
# pytest                # Run tests
# black lespell tests   # Format code
# ruff check            # Lint code
# mypy lespell          # Type checking
