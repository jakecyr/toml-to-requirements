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

toml_poetry = """
[tool.poetry]
name = "toml_to_requirements"
version = "0.2.2"
description = "Convert a pyproject.toml file to a requirements.txt file"
authors = ["Jake Cyr <cyrjake@gmail.com>"]
license = "MIT"
readme = "README.md"
keywords = ["toml", "requirements", "converter", "parser"]
classifiers = [
  "Intended Audience :: Developers",
  "License :: OSI Approved :: MIT License",
  "Programming Language :: Python :: 3",
]
packages = [{ include = "toml_to_requirements" }]

[tool.poetry.dependencies]
python = ">=3.9,<4.0"
toml = "^0.10.2"

[tool.poetry.group.dev]
optional = true

[tool.poetry.group.dev.dependencies]
ruff = "^0.3.5"
mypy = "^1.9.0"

[tool.poetry.group.test.dependencies]
pytest = "^8.1.1"
coverage = "^7.4.4"
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


def test_with_poetry_content_and_flag_returns_expected_output() -> None:
    result: str = convert_toml_to_requirements(
        toml_poetry,
        optional_lists=None,
        poetry=True,
    )

    assert result == "toml ~= 0.10.2"


def test_with_poetry_content_and_flag_with_optional_list_returns_expected_output() -> (
    None
):
    result: str = convert_toml_to_requirements(
        toml_poetry,
        optional_lists=["dev"],
        poetry=True,
    )
    expected_packages: list[str] = sorted(
        [
            "mypy ~= 1.9.0",
            "ruff ~= 0.3.5",
            "toml ~= 0.10.2",
        ]
    )

    assert result == "\n".join(expected_packages)


def test_with_poetry_content_and_flag_with_optional_lists_returns_expected_output() -> (
    None
):
    result: str = convert_toml_to_requirements(
        toml_poetry,
        optional_lists=["dev", "test"],
        poetry=True,
    )
    expected_packages: list[str] = sorted(
        [
            "mypy ~= 1.9.0",
            "ruff ~= 0.3.5",
            "toml ~= 0.10.2",
            "coverage ~= 7.4.4",
            "pytest ~= 8.1.1",
        ]
    )

    assert result == "\n".join(expected_packages)


def test_with_poetry_content_and_flag_with_nonexistent_optional_lists_returns_expected_output() -> (
    None
):
    result: str = convert_toml_to_requirements(
        toml_poetry,
        optional_lists=["dev", "test", "something-else"],
        poetry=True,
    )
    expected_packages: list[str] = sorted(
        [
            "mypy ~= 1.9.0",
            "ruff ~= 0.3.5",
            "toml ~= 0.10.2",
            "coverage ~= 7.4.4",
            "pytest ~= 8.1.1",
        ]
    )

    assert result == "\n".join(expected_packages)
