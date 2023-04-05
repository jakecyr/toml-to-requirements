# TOML to Requirements

Simple script to convert a pyproject.toml file to a requirements.txt file.

Does not support poetry projects! They have their own converter tools.

## Installation

Install with pip:

```bash
pip install toml-to-requirements
```

## Usage

Run the following command to generate a requirements.txt file without including optional dependencies:

```bash
toml-to-req --toml-file pyproject.toml
```

To include optional dependencies, include the `--include-optional` flag in the above command:

```bash
toml-to-req --toml-file pyproject.toml --include-optional
```
