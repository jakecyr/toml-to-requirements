"""Convert a pyproject.toml file to a requirements.txt file."""

from __future__ import annotations
from typing import Any

import toml


def _convert_setuptools_to_requirements(
    parsed_toml_file: dict[str, Any],
    *,
    optional_lists: list[str] | None,
) -> str:
    project: dict | None = parsed_toml_file.get("project")

    if project is None:
        raise RuntimeError(
            "The project section is missing from the TOML file. Exiting..."
        )

    dependencies = set(project.get("dependencies", []))

    if optional_lists is not None:
        optional_dependency_list: dict[str, Any] = project.get(
            "optional-dependencies", {}
        )
        optional_lists_to_include: set[str] = (
            set(optional_lists) if optional_lists is not None else set()
        )

        for optional_list, deps in optional_dependency_list.items():
            if optional_list in optional_lists_to_include:
                dependencies.update(deps)

    return "\n".join(sorted(dependencies))


def convert_toml_to_requirements(
    toml_file_string: str,
    *,
    optional_lists: list[str] | None,
    poetry: bool,
) -> str:
    """Convert a pyproject.toml file to a requirements.txt file.

    Args:
        toml_file_string: The contents of the pyproject.toml file.
        optional_lists: A list of optional dependency lists to include.
        poetry: Whether to use poetry instead of setuptools.

    Returns:
        The contents of the requirements.txt file.

    Raises:
        RuntimeError: If poetry is set to True since it is not yet supported.
    """
    if poetry:
        raise RuntimeError("Poetry is not yet supported.")

    parsed_toml_file: dict[str, Any] = toml.loads(toml_file_string)

    return _convert_setuptools_to_requirements(
        parsed_toml_file,
        optional_lists=optional_lists,
    )
