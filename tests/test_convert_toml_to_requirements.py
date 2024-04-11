from __future__ import annotations
import pytest
from toml_to_requirements.convert_toml_to_requirements import (
    convert_toml_to_requirements,
)

# Test data for a bad file.
toml_content_bad = """
[bad]
dependencies = [
    "requests",
    "flask",
]
"""


# Test data for a simple TOML file
toml_content_basic = """
[project]
dependencies = [
    "requests",
    "flask",
]
"""

# Test data for a TOML file with optional dependencies
toml_content_with_optional = """
[project]
dependencies = [
    "requests",
]
[project.optional-dependencies]
dev = [
    "pytest",
    "black",
]
"""


def test_with_invalid_file_format_raise_runtime_error() -> None:
    with pytest.raises(RuntimeError):
        convert_toml_to_requirements(
            toml_content_bad,
            optional_lists=None,
            poetry=False,
        )


def test_basic_conversion() -> None:
    expected_output = "flask\nrequests"
    result: str = convert_toml_to_requirements(
        toml_content_basic,
        optional_lists=None,
        poetry=False,
    )
    assert result == expected_output


def test_including_optional_dependencies() -> None:
    expected_output = "black\npytest\nrequests"
    result: str = convert_toml_to_requirements(
        toml_content_with_optional,
        optional_lists=["dev"],
        poetry=False,
    )
    assert result == expected_output


def test_excluding_unknown_optional_dependencies() -> None:
    expected_output = "flask\nrequests"
    result: str = convert_toml_to_requirements(
        toml_content_basic,
        optional_lists=["dev"],
        poetry=False,
    )
    assert result == expected_output


def test_excluding_unspecified_optional_dependencies() -> None:
    expected_output = "requests"
    result: str = convert_toml_to_requirements(
        toml_content_with_optional,
        optional_lists=[],
        poetry=False,
    )
    assert result == expected_output


def test_poetry_not_supported_error() -> None:
    with pytest.raises(RuntimeError, match="Poetry is not yet supported") as exc_info:
        convert_toml_to_requirements(
            toml_content_basic,
            optional_lists=None,
            poetry=True,
        )
    assert "Poetry is not yet supported." in str(exc_info.value)
