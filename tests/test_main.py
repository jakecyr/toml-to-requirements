from __future__ import annotations
from toml_to_requirements.main import main
from toml_to_requirements.cli import CLIArguments
from pathlib import Path
from unittest import mock

EXAMPLE_TOML_PATH_WITH_VERSIONS = Path("tests/example_toml_with_versions.toml")
EXAMPLE_REQUIREMENTS_PATH_WITH_VERSIONS = Path(
    "tests/example_requirements_with_versions.txt"
)

EXAMPLE_TOML_PATH = Path("tests/example_toml.toml")
EXAMPLE_REQUIREMENTS_PATH = Path("tests/example_requirements.txt")


@mock.patch(
    "toml_to_requirements.main.get_parsed_arguments",
    return_value=CLIArguments(
        toml_file_path=EXAMPLE_TOML_PATH,
        requirements_file_path=EXAMPLE_REQUIREMENTS_PATH,
        optional_lists=["dev"],
        poetry=False,
    ),
)
def test_main_with_simple_toml(_mock_get_parsed_arguments: mock.Mock) -> None:
    try:
        main()

        assert EXAMPLE_REQUIREMENTS_PATH.is_file()

        with EXAMPLE_REQUIREMENTS_PATH.open("r") as f:
            requirements_content: str = f.read()

        packages_in_requirements = set(requirements_content.split("\n"))

        assert "black" in packages_in_requirements
        assert "toml" in packages_in_requirements
        assert len(packages_in_requirements) == 2
    finally:
        EXAMPLE_REQUIREMENTS_PATH.unlink(missing_ok=True)


@mock.patch(
    "toml_to_requirements.main.get_parsed_arguments",
    return_value=CLIArguments(
        toml_file_path=EXAMPLE_TOML_PATH_WITH_VERSIONS,
        requirements_file_path=EXAMPLE_REQUIREMENTS_PATH_WITH_VERSIONS,
        optional_lists=["dev"],
        poetry=False,
    ),
)
def test_main_with_versions_in_toml(_mock_get_parsed_arguments: mock.Mock) -> None:
    try:
        main()

        assert EXAMPLE_REQUIREMENTS_PATH_WITH_VERSIONS.is_file()

        with EXAMPLE_REQUIREMENTS_PATH_WITH_VERSIONS.open("r") as f:
            requirements_content: str = f.read()

        packages_in_requirements = set(requirements_content.split("\n"))

        assert "black>=3.1,<4.0" in packages_in_requirements
        assert "toml==2.0" in packages_in_requirements
        assert len(packages_in_requirements) == 2
    finally:
        EXAMPLE_REQUIREMENTS_PATH_WITH_VERSIONS.unlink(missing_ok=True)
