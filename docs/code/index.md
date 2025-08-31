# Modules


## Overview

These are the modules used in the docstring-format-checker package:

| Module                        | Description                                                                                                                                                                                                                            |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Core](./core.md)             | The `core` module contains the main `DocstringChecker` class responsible for parsing Python files with AST, extracting docstrings from functions/classes/methods, and validating them against configured section requirements.         |
| [Configuration](./config.md)  | The `config` module handles loading and validating configuration from TOML files. It supports automatic discovery of `pyproject.toml` files and defines section validation rules through the `SectionConfig` dataclass.                |
| [CLI](./cli.md)               | The `cli` module provides the command-line interface using Typer. It supports both `docstring-format-checker` and `dfc` entry points with subcommands for checking files/directories and generating configuration examples.            |
| [Exceptions](./exceptions.md) | The `exceptions` module defines custom exception classes for structured error handling, including `DocstringError` for validation failures, `InvalidFileError` for non-Python files, and `DirectoryNotFoundError` for path validation. |


## Key Features

- **AST-based parsing**: Uses Python's AST module for robust code analysis
- **Configurable validation**: TOML-based configuration with 4 section types: `free_text`, `list_name`, `list_type`, `list_name_and_type`
- **Hierarchical config discovery**: Automatically finds configuration in `pyproject.toml` files
- **Rich output formatting**: Uses Rich library for colored console output and error tables
- **Dual CLI entry points**: Available as both `docstring-format-checker` and `dfc`
- **Comprehensive error handling**: Custom exceptions for different failure scenarios


## Section Types

The checker supports four types of docstring sections:

1. **`free_text`**: Admonition-style sections like summary, details, examples
2. **`list_name`**: Simple name lists
3. **`list_type`**: Type-only lists for raises, yields sections
4. **`list_name_and_type`**: Name and type lists for parameters, returns sections


## Testing

This package maintains 100% test coverage with comprehensive testing against:

1. **Unit tests**: Complete test coverage for all modules and functions
2. **Integration tests**: CLI and end-to-end workflow testing
3. **Configuration tests**: TOML parsing and validation testing
4. **Error handling tests**: Exception scenarios and edge cases
5. **AST parsing tests**: Python code analysis and docstring extraction

Tests are run in matrix against:

1. **Python Versions**:
   - `3.10`
   - `3.11`
   - `3.12`
   - `3.13`
2. **Operating Systems**:
   - `ubuntu-latest`
   - `windows-latest`
   - `macos-latest`


## Coverage

<div style="position:relative; border:none; width:100%; height:100%; display:block; overflow:auto;">
    <iframe src="./coverage/index.html" style="width:100%; height:600px;"></iframe>
</div>
