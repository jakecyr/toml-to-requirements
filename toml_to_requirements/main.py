#!/usr/bin/env

import toml
import sys


def main():
    data = toml.load("pyproject.toml")

    project = data.get("project")

    if project is None:
        print("project section is missing from the toml file. Exiting...")
        sys.exit(1)

    dependencies = set(project.get("dependencies", []))
    optional_dependency_list = project.get("optional-dependencies", [])

    for optional_list in optional_dependency_list:
        optional_dependencies = optional_dependency_list[optional_list]
        dependencies.update(optional_dependencies)

    REQUIREMENTS_CONTENT = "\n".join(sorted(dependencies))

    with open("requirements.txt", "w") as f:
        f.write(REQUIREMENTS_CONTENT)


if __name__ == "__main__":
    main()
