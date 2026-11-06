"""Convert supported pyproject.toml dependencies to pip requirements."""

from __future__ import annotations

import re
from typing import Any

import toml
from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name


def _validate_requirement(value: str) -> str:
    if not isinstance(value, str) or "\n" in value or "\r" in value:
        raise ValueError(f"Invalid requirement: {value!r}")
    try:
        Requirement(value)
    except InvalidRequirement as exc:
        raise ValueError(f"Invalid requirement: {value!r}") from exc
    return value


def _poetry_constraint(constraint: str) -> str:
    """Translate Poetry's common version syntax to PEP 440 specifiers."""
    parts: list[str] = []
    for raw in constraint.split(","):
        part = raw.strip()
        match = re.fullmatch(r"([\^~])(\d+(?:\.\d+)*)", part)
        if match:
            operator, version = match.groups()
            numbers = [int(n) for n in version.split(".")]
            if operator == "^":
                index = next((i for i, n in enumerate(numbers) if n), len(numbers) - 1)
            else:
                index = 0 if len(numbers) == 1 else 1
            upper = numbers[: index + 1]
            upper[index] += 1
            parts.extend((f">={version}", "<" + ".".join(map(str, upper))))
        elif part == "*":
            continue
        elif re.fullmatch(r"\d+(?:\.\d+)*(?:\.\*)?", part):
            parts.append(f"=={part}")
        elif (
            part
            and not any(c in part for c in "^| ")
            and ("~" not in part or part.startswith("~="))
        ):
            parts.append(part)
        else:
            raise ValueError(f"Unsupported Poetry version constraint: {constraint!r}")
    return ",".join(parts)


def _poetry_requirement(name: str, value: Any) -> str:
    if isinstance(value, str):
        spec, extras, marker = value, [], None
    elif isinstance(value, dict):
        unsupported = set(value) - {"version", "extras", "markers", "optional"}
        if unsupported:
            raise ValueError(
                f"Unsupported Poetry fields for {name}: {', '.join(sorted(unsupported))}"
            )
        spec = value.get("version", "*")
        extras = value.get("extras", [])
        marker = value.get("markers")
        if (
            not isinstance(spec, str)
            or not isinstance(extras, list)
            or not all(isinstance(x, str) for x in extras)
            or (marker is not None and not isinstance(marker, str))
        ):
            raise ValueError(f"Invalid Poetry dependency: {name}")
    else:
        raise ValueError(f"Unsupported Poetry dependency: {name}")  # noqa: TRY004
    suffix = f"[{','.join(extras)}]" if extras else ""
    requirement = f"{name}{suffix}{_poetry_constraint(spec)}"
    if marker:
        requirement += f"; {marker}"
    return _validate_requirement(requirement)


def _convert_poetry_to_requirements(
    parsed: dict[str, Any], *, optional_lists: list[str] | None
) -> str:
    project = parsed.get("tool", {}).get("poetry")
    if not isinstance(project, dict):
        raise RuntimeError("The [tool.poetry] section is missing from the TOML file.")  # noqa: TRY004
    selected = set(optional_lists or [])
    extras = project.get("extras", {})
    enabled = {
        canonicalize_name(name) for extra in selected for name in extras.get(extra, [])
    }
    dependencies = set()
    for name, value in project.get("dependencies", {}).items():
        if name.lower() == "python":
            continue
        if (
            isinstance(value, dict)
            and value.get("optional", False)
            and canonicalize_name(name) not in enabled
        ):
            continue
        dependencies.add(_poetry_requirement(name, value))
    for group_name in selected:
        group = project.get("group", {}).get(group_name, {})
        for name, value in group.get("dependencies", {}).items():
            dependencies.add(_poetry_requirement(name, value))
    return "\n".join(sorted(dependencies))


def _convert_setuptools_to_requirements(
    parsed: dict[str, Any], *, optional_lists: list[str] | None
) -> str:
    project = parsed.get("project")
    if not isinstance(project, dict):
        raise RuntimeError("The [project] section is missing from the TOML file.")  # noqa: TRY004
    if "dependencies" in project.get("dynamic", []) or (
        optional_lists and "optional-dependencies" in project.get("dynamic", [])
    ):
        raise ValueError(
            "Dynamic dependencies cannot be converted from pyproject.toml."
        )
    dependencies = {
        _validate_requirement(dep) for dep in project.get("dependencies", [])
    }
    for name in optional_lists or []:
        dependencies.update(
            _validate_requirement(dep)
            for dep in project.get("optional-dependencies", {}).get(name, [])
        )
    return "\n".join(sorted(dependencies))


def convert_toml_to_requirements(
    toml_file_string: str, *, optional_lists: list[str] | None, poetry: bool
) -> str:
    """Return sorted, deduplicated pip requirements from TOML source text.

    Unknown optional list names are ignored. Invalid TOML, requirements, and
    unsupported Poetry syntax raise an exception instead of producing bad output.
    """
    parsed = toml.loads(toml_file_string)
    if poetry:
        return _convert_poetry_to_requirements(parsed, optional_lists=optional_lists)
    return _convert_setuptools_to_requirements(parsed, optional_lists=optional_lists)
