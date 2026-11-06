# TOML to Requirements

Convert dependencies declared in `pyproject.toml` into a sorted, deduplicated pip requirements file. Python 3.9–3.15 is supported.

## Install and use

```sh
python -m pip install toml-to-requirements
toml-to-req --toml-file pyproject.toml --requirements-file requirements.txt
```

Both paths are optional and default to `pyproject.toml` and `requirements.txt`. The output file is replaced after conversion succeeds. Input and output must be different files. Pass comma-separated names to include optional dependency lists:

```sh
toml-to-req -t pyproject.toml -r requirements-dev.txt -o dev,test
```

By default, the tool reads PEP 621 `[project].dependencies` and selected `[project.optional-dependencies]`. Requirement strings, including environment markers and URLs, are preserved. Unknown optional names are ignored. Dynamic dependency lists cannot be resolved and cause an error when requested.

For legacy Poetry metadata, add `--poetry` (or `-p`):

```sh
toml-to-req --poetry --optional-lists dev,feature
```

This reads `[tool.poetry.dependencies]` and the named Poetry groups and extras. Common version constraints, including caret and tilde constraints, are translated to pip-compatible specifiers. Optional dependencies are included when their extra is selected. Dependency tables support `version`, `extras`, `markers`, and `optional`. Other Poetry features, including Git/path/URL sources, Python-specific constraints, multiple constraint alternatives, and `||`, are rejected rather than silently producing invalid output. Use Poetry's export tooling if you need those features or a resolved, locked set of transitive dependencies. This tool exports declarations; it does not resolve versions or generate hashes.

The Python API returns the file contents as a string:

```python
from toml_to_requirements.convert_toml_to_requirements import (
    convert_toml_to_requirements,
)

requirements = convert_toml_to_requirements(
    '[project]\ndependencies = ["requests>=2"]',
    optional_lists=None,
    poetry=False,
)
```

## Development

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```sh
uv sync --locked
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy toml_to_requirements
uv run --locked coverage run --source toml_to_requirements -m pytest
uv run --locked coverage report --fail-under=90 --show-missing
```

CI runs these checks across Python 3.9–3.15. To test another interpreter locally, run `uv sync --locked --python 3.15` before the checks. Run `uv build` to build the source distribution and wheel.

## License

MIT
