#!/usr/bin/env

import toml
import sys
import argparse


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--toml-file", type=str, default="pyproject.toml")
    argparser.add_argument("--include-optional", action="store_true")
    argparser.add_argument(
        "-o", "--optional-lists", help="Optional dependency lists to include."
    )

    args = argparser.parse_args()

    data = toml.load(args.toml_file)

    project = data.get("project")

    if project is None:
        print("project section is missing from the toml file. Exiting...")
        sys.exit(1)

    dependencies = set(project.get("dependencies", []))

    if args.include_optional:
        optional_dependency_list = project.get("optional-dependencies", [])
        optional_lists_to_include = (
            None if args.optional_lists is None else str(args.optional_lists).split(",")
        )

        for optional_list in optional_dependency_list:
            if (
                optional_lists_to_include is not None
                and optional_list not in optional_lists_to_include
            ):
                continue

            optional_dependencies = optional_dependency_list[optional_list]
            dependencies.update(optional_dependencies)

    requirements_content = "\n".join(sorted(dependencies))

    with open("requirements.txt", "w") as f:
        f.write(requirements_content)


if __name__ == "__main__":
    main()
