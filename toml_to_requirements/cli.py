from __future__ import annotations
import argparse
from pathlib import Path
from typing import NamedTuple


class CLIArguments(NamedTuple):
    toml_file_path: Path
    requirements_file_path: Path
    optional_lists: list[str] | None
    poetry: bool = False


def get_parsed_arguments() -> CLIArguments:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--toml-file",
        "-t",
        type=str,
        default="pyproject.toml",
        help="The path of the pyproject.toml file to convert.",
    )
    parser.add_argument(
        "--requirements-file",
        "-r",
        type=str,
        default="requirements.txt",
        help="The path of the requirements file to generate.",
    )
    parser.add_argument(
        "--poetry",
        "-p",
        help="If the TOML file is a poetry project.",
        action="store_true",
    )
    parser.add_argument(
        "-o",
        "--optional-lists",
        help="Comma separated optional dependency lists (or poetry extras / groups) to include.",
    )
    args: argparse.Namespace = parser.parse_args()

    return CLIArguments(
        toml_file_path=Path(args.toml_file),
        requirements_file_path=Path(args.requirements_file),
        optional_lists=args.optional_lists.split(",") if args.optional_lists else None,
        poetry=args.poetry or False,
    )
