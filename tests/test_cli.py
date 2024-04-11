from __future__ import annotations
from pathlib import Path
from unittest.mock import patch
from toml_to_requirements.cli import (
    CLIArguments,
    get_parsed_arguments,
)


def test_default_arguments() -> None:
    with patch("sys.argv", ["prog"]):
        args: CLIArguments = get_parsed_arguments()
        assert args.toml_file_path == Path("pyproject.toml")
        assert args.poetry is False
        assert args.optional_lists is None


def test_specifying_toml_file() -> None:
    with patch("sys.argv", ["prog", "--toml-file", "custom.toml"]):
        args: CLIArguments = get_parsed_arguments()
        assert args.toml_file_path == Path("custom.toml")


def test_using_poetry_and_specifying_optional_lists() -> None:
    with patch("sys.argv", ["prog", "--poetry", "--optional-lists", "dev,prod"]):
        args: CLIArguments = get_parsed_arguments()
        assert args.poetry is True
        assert args.optional_lists == ["dev", "prod"]


def test_optional_lists_splitting() -> None:
    with patch("sys.argv", ["prog", "-o", "dev,prod"]):
        args: CLIArguments = get_parsed_arguments()
        assert args.optional_lists == ["dev", "prod"]
