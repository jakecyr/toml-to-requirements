from __future__ import annotations

import pytest
import toml

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

    assert result == "toml>=0.10.2,<0.11"


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
            "mypy>=1.9.0,<2",
            "ruff>=0.3.5,<0.4",
            "toml>=0.10.2,<0.11",
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
            "mypy>=1.9.0,<2",
            "ruff>=0.3.5,<0.4",
            "toml>=0.10.2,<0.11",
            "coverage>=7.4.4,<8",
            "pytest>=8.1.1,<9",
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
            "mypy>=1.9.0,<2",
            "ruff>=0.3.5,<0.4",
            "toml>=0.10.2,<0.11",
            "coverage>=7.4.4,<8",
            "pytest>=8.1.1,<9",
        ]
    )

    assert result == "\n".join(expected_packages)


@pytest.mark.parametrize(
    ("constraint", "expected"),
    [
        ("^1.2.3", ">=1.2.3,<2"),
        ("^0.2.3", ">=0.2.3,<0.3"),
        ("^0.0.3", ">=0.0.3,<0.0.4"),
        ("~1.2.3", ">=1.2.3,<1.3"),
        ("~1", ">=1,<2"),
        ("1.2", "==1.2"),
        ("1.2.*", "==1.2.*"),
        ("*", ""),
        (">=1, <2", ">=1,<2"),
    ],
)
def test_poetry_constraints(constraint: str, expected: str) -> None:
    result = convert_toml_to_requirements(
        f'[tool.poetry.dependencies]\nexample = "{constraint}"',
        optional_lists=None,
        poetry=True,
    )
    assert result == f"example{expected}"


def test_poetry_optional_extras_and_table_dependencies() -> None:
    content = """
[tool.poetry.dependencies]
python = "^3.9"
foo = {version = "^2.1", extras = ["fast"], markers = "sys_platform == 'linux'"}
bar = {version = "1.0", optional = true}
[tool.poetry.extras]
feature = ["bar"]
[tool.poetry.group.dev.dependencies]
pytest = "*"
"""
    assert (
        convert_toml_to_requirements(content, optional_lists=None, poetry=True)
        == "foo[fast]>=2.1,<3; sys_platform == 'linux'"
    )
    assert convert_toml_to_requirements(
        content, optional_lists=["feature", "dev"], poetry=True
    ).splitlines() == [
        "bar==1.0",
        "foo[fast]>=2.1,<3; sys_platform == 'linux'",
        "pytest",
    ]


@pytest.mark.parametrize(
    "value",
    ['"^1 || ^2"', '{git = "https://example.com/repo.git"}', '[{version = "^1"}]'],
)
def test_unsupported_poetry_syntax_fails(value: str) -> None:
    with pytest.raises(ValueError, match="Unsupported"):
        convert_toml_to_requirements(
            f"[tool.poetry.dependencies]\nfoo = {value}",
            optional_lists=None,
            poetry=True,
        )


def test_pep621_requirements_are_preserved_and_deduplicated() -> None:
    content = """
[project]
dependencies = ["foo[bar]>=1; python_version >= '3.9'", "foo[bar]>=1; python_version >= '3.9'"]
[project.optional-dependencies]
test = ["other @ https://example.com/other.whl"]
"""
    result = convert_toml_to_requirements(
        content, optional_lists=["test", "missing"], poetry=False
    )
    assert result.splitlines() == [
        "foo[bar]>=1; python_version >= '3.9'",
        "other @ https://example.com/other.whl",
    ]


def test_dynamic_dependencies_and_invalid_requirements_fail() -> None:
    with pytest.raises(ValueError, match="Dynamic"):
        convert_toml_to_requirements(
            '[project]\ndynamic = ["dependencies"]', optional_lists=None, poetry=False
        )
    with pytest.raises(ValueError, match="Invalid requirement"):
        convert_toml_to_requirements(
            '[project]\ndependencies = ["foo^1"]', optional_lists=None, poetry=False
        )


def test_invalid_toml_fails() -> None:
    with pytest.raises(toml.TomlDecodeError):
        convert_toml_to_requirements("[project", optional_lists=None, poetry=False)
