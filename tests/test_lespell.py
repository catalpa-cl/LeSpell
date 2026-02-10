"""
Tests for the lespell package initialization.
"""

import lespell


def test_package_version():
    """Test that the package version is set."""
    assert hasattr(lespell, "__version__")
    assert lespell.__version__ == "0.1.0"


def test_package_has_modules():
    """Test that the package has the expected modules."""
    assert hasattr(lespell, "__all__")
    expected_modules = ["data_prep", "analysis", "languagetool"]
    assert all(module in lespell.__all__ for module in expected_modules)
