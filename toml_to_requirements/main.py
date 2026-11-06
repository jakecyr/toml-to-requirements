"""Main entry point for the CLI."""

from __future__ import annotations

from toml_to_requirements.cli import CLIArguments, get_parsed_arguments
from toml_to_requirements.convert_toml_to_requirements import (
    convert_toml_to_requirements,
)


def main() -> None:
    arguments: CLIArguments = get_parsed_arguments()

    if not arguments.toml_file_path.is_file():
        raise FileNotFoundError(f"File not found: {arguments.toml_file_path}")

    if arguments.toml_file_path.resolve() == arguments.requirements_file_path.resolve():
        raise ValueError("Input and output paths must be different.")

    with arguments.toml_file_path.open("r", encoding="utf-8") as f:
        toml_file_contents: str = f.read()

    requirements_content: str = convert_toml_to_requirements(
        toml_file_contents,
        optional_lists=arguments.optional_lists,
        poetry=arguments.poetry,
    )

    with arguments.requirements_file_path.open("w", encoding="utf-8") as f:
        f.write(requirements_content)
