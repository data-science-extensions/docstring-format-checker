<h1 align="center"><u><code>docstring-format-checker</code></u></h1>

<p align="center">
<a href="https://github.com/data-science-extensions/docstring-format-checker/releases">
    <img src="https://img.shields.io/github/v/release/data-science-extensions/docstring-format-checker?logo=github" alt="github-release"></a>
<a href="https://pypi.org/project/docstring-format-checker">
    <img src="https://img.shields.io/pypi/implementation/docstring-format-checker?logo=pypi&logoColor=ffde57" alt="implementation"></a>
<a href="https://pypi.org/project/docstring-format-checker">
    <img src="https://img.shields.io/pypi/v/docstring-format-checker?label=version&logo=python&logoColor=ffde57&color=blue" alt="version"></a>
<a href="https://pypi.org/project/docstring-format-checker">
    <img src="https://img.shields.io/pypi/pyversions/docstring-format-checker?logo=python&logoColor=ffde57" alt="python-versions"></a>
<br>
<a href="https://github.com/data-science-extensions/docstring-format-checker/actions/workflows/ci.yml">
    <img src="https://img.shields.io/static/v1?label=os&message=ubuntu+|+macos+|+windows&color=blue&logo=ubuntu&logoColor=green" alt="os"></a>
<a href="https://pypi.org/project/docstring-format-checker">
    <img src="https://img.shields.io/pypi/status/docstring-format-checker?color=green" alt="pypi-status"></a>
<a href="https://pypi.org/project/docstring-format-checker">
    <img src="https://img.shields.io/pypi/format/docstring-format-checker?color=green" alt="pypi-format"></a>
<a href="https://github.com/data-science-extensions/docstring-format-checker/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/data-science-extensions/docstring-format-checker?color=green" alt="github-license"></a>
<a href="https://piptrends.com/package/docstring-format-checker">
    <img src="https://img.shields.io/pypi/dm/docstring-format-checker?color=green" alt="pypi-downloads"></a>
<a href="https://codecov.io/gh/data-science-extensions/docstring-format-checker">
    <img src="https://codecov.io/gh/data-science-extensions/docstring-format-checker/graph/badge.svg" alt="codecov-repo"></a>
<a href="https://github.com/psf/black">
    <img src="https://img.shields.io/static/v1?label=style&message=black&color=black&logo=windows-terminal&logoColor=white" alt="style"></a>
<br>
<a href="https://github.com/data-science-extensions/docstring-format-checker">
    <img src="https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat" alt="contributions"></a>
<br>
<a href="https://github.com/data-science-extensions/docstring-format-checker/actions/workflows/ci.yml">
    <img src="https://github.com/data-science-extensions/docstring-format-checker/actions/workflows/ci.yml/badge.svg?event=pull_request" alt="CI"></a>
<a href="https://github.com/data-science-extensions/docstring-format-checker/actions/workflows/cd.yml">
    <img src="https://github.com/data-science-extensions/docstring-format-checker/actions/workflows/cd.yml/badge.svg?event=release" alt="CD"></a>
</p>


### 📝 Introduction

A powerful Python CLI tool that validates docstring formatting and completeness using AST parsing. Ensure consistent, high-quality documentation across your entire codebase with configurable validation rules and rich terminal output.

**Key Features:**

- 🔍 **AST-based parsing** - Robust code analysis without regex fragility
- ⚙️ **Configurable validation** - Four section types with TOML-based configuration
- 📚 **Flexible section ordering** - Support for unordered "floating" sections
- 📁 **Hierarchical config discovery** - Automatic `pyproject.toml` detection
- 🎨 **Rich terminal output** - Beautiful colored output and error tables
- 🚀 **Dual CLI entry points** - Use `docstring-format-checker` or `dfc`
- 🛡️ **100% test coverage** - Thoroughly tested and reliable


### 🚀 Quick Start

```bash
# Install
uv add docstring-format-checker

# Check a single file
dfc --check my_module.py

# Check entire directory
dfc --check src/

# Generate example configuration
dfc --example=config
```


### 🔗 Key URLs

For reference, these URLs are used:

| Type           | Source | URL                                                                    |
| -------------- | ------ | ---------------------------------------------------------------------- |
| Git Repo       | GitHub | https://github.com/data-science-extensions/docstring-format-checker    |
| Python Package | PyPI   | https://pypi.org/project/docstring-format-checker                      |
| Package Docs   | Pages  | https://data-science-extensions.com/toolboxes/docstring-format-checker |


### 📂 Section Types

Configure validation for four types of docstring sections:

| Type                 | Description               | Example Use                    |
| -------------------- | ------------------------- | ------------------------------ |
| `free_text`          | Admonition-style sections | Summary, details, examples     |
| `list_name`          | Simple name lists         | Simple parameter lists         |
| `list_type`          | Type-only lists           | Raises, yields sections        |
| `list_name_and_type` | Name and type lists       | Parameters, returns with types |


### ⚙️ Configuration

Create a `pyproject.toml` with your validation rules. The `order` attribute is optional; sections without an order (like "deprecation warning") can appear anywhere in the docstring.

You can utilise a layout in separate blocks like this:

```toml
[tool.dfc]

[[tool.dfc.sections]]
order = 1
name = "summary"
type = "free_text"
admonition = "note"
prefix = "!!!"
required = true

[[tool.dfc.sections]]
order = 2
name = "params"
type = "list_name_and_type"
required = true

# Unordered section - can appear anywhere
[[tool.dfc.sections]]
name = "deprecation warning"
type = "free_text"
admonition = "deprecation"
prefix = "!!!"
required = false

[[tool.dfc.sections]]
order = 3
name = "returns"
type = "list_name_and_type"
required = false
```

Or like this in a single block:

```toml
[tool.dfc]
# or [tool.docstring-format-checker]
allow_undefined_sections = false
require_docstrings = true
check_private = true
validate_param_types = true
optional_style = "validate"  # "silent", "validate", or "strict"
sections = [
    { order = 1, name = "summary",  type = "free_text",          required = true, admonition = "note", prefix = "!!!" },
    { order = 2, name = "details",  type = "free_text",          required = false, admonition = "abstract", prefix = "???+" },
    { order = 3, name = "params",   type = "list_name_and_type", required = false },
    { order = 4, name = "raises",   type = "list_type",          required = false },
    { order = 5, name = "returns",  type = "list_name_and_type", required = false },
    { order = 6, name = "yields",   type = "list_type",          required = false },
    { order = 7, name = "examples", type = "free_text",          required = false, admonition = "example", prefix = "???+" },
    { order = 8, name = "notes",    type = "free_text",          required = false, admonition = "note", prefix = "???" },
]
```


### 📥 Installation

You can install and use this package multiple ways by using any of your preferred methods: [`pip`][pip], [`pipenv`][pipenv], [`poetry`][poetry], or [`uv`][uv].


#### Using [`pip`][pip]:

1. In your terminal, run:

    ```sh
    python3 -m pip install --upgrade pip
    python3 -m pip install docstring-format-checker
    ```

2. Or, in your `requirements.txt` file, add:

    ```txt
    docstring-format-checker
    ```

    Then run:

    ```sh
    python3 -m pip install --upgrade pip
    python3 -m pip install --requirement=requirements.txt
    ```


#### Using [`pipenv`][pipenv]:

1. Install using environment variables:

    In your `Pipfile` file, add:

    ```toml
    [[source]]
    url = "https://pypi.org/simple"
    verify_ssl = false
    name = "pypi"

    [packages]
    docstring-format-checker = "*"
    ```

    Then run:

    ```sh
    python3 -m pip install pipenv
    python3 -m pipenv install --verbose --skip-lock --categories=root index=pypi docstring-format-checker
    ```

2. Or, in your `requirements.txt` file, add:

    ```sh
    docstring-format-checker
    ```

    Then run:

    ```sh
    python3 -m pipenv install --verbose --skip-lock --requirements=requirements.txt
    ```

3. Or just run this:

    ```sh
    python3 -m pipenv install --verbose --skip-lock docstring-format-checker
    ```


#### Using [`poetry`][poetry]:

1. In your `pyproject.toml` file, add:

    ```toml
    [project]
    dependencies = [
        "docstring-format-checker==1.*",
    ]
    ```

    Then run:

    ```sh
    poetry sync
    poetry install
    ```

2. Or just run this:

    ```sh
    poetry add "docstring-format-checker==1.*"
    poetry sync
    poetry install
    ```


#### Using [`uv`][uv]:

1. In your `pyproject.toml` file, add:

    ```toml
    [project]
    dependencies = [
        "docstring-format-checker==1.*",
    ]
    ```

   Then run:

   ```sh
   uv sync
   ```

2. Or run this:

    ```sh
    uv add "docstring-format-checker==1.*"
    uv sync
    ```

3. Or just run this:

    ```sh
    uv pip install "docstring-format-checker==1.*"
    ```


### 💡 Usage Examples

```bash
# Check a single Python file
dfc --check src/my_module.py

# Check multiple Python files
dfc file1.py file2.py

# Check entire directory recursively
dfc --check src/

# Check with table output format
dfc --output=table src/

# Generate example configuration file
dfc --example=config > pyproject.toml
```


#### Advanced Configuration

```bash
# Use custom config file location
dfc --config=custom_config.toml src/

# Exclude specific files using glob patterns
dfc src/ --exclude "**/test_*.py"

# Stop on first failure (CI environments)
dfc --check src/

# Suppress non-error output
dfc --quiet src/
```


#### Integration with CI/CD

```yaml
# .github/workflows/docs.yml
name: Documentation Quality
on: [push, pull_request]

jobs:
  docstring-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv pip install docstring-format-checker
      - run: dfc --check src/
```


#### Integration with Pre-commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/data-science-extensions/docstring-format-checker
    rev: "v1.11.3"
    hooks:
    -   id: docstring-format-checker
        name: Docstring Format Checker
        entry: dfc --check
```


### 📋 Example Output


#### Standard List Output

The option `output=list` is the default:

```sh
dfc --check src/models/user.py
```

Or you can declare it explicitly:

```sh
dfc --check --output=list src/models/user.py
```

Which returns:

```text
src/models/user.py
  Line 12 - function 'create_user':
    - Missing required section: 'params'
  Line 45 - function 'delete_user':
    - Missing required section: 'returns'

Found 2 error(s) in 2 functions over 1 file
```


#### Table Output Format

```sh
dfc --check --output=table src/models/user.py
```

```text
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ File               ┃ Line ┃ Item        ┃ Type     ┃ Error                            ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ src/models/user.py │   12 │ create_user │ function │ - Missing required section:      │
│                    │      │             │          │ 'params'.                        │
│                    │   45 │ delete_user │ function │ - Missing required section:      │
│                    │      │             │          │ 'returns'.                       │
└────────────────────┴──────┴─────────────┴──────────┴──────────────────────────────────┘

Found 2 error(s) in 2 functions over 1 file
```


### 🏗️ Architecture

The tool follows a clean, modular architecture:

- **`core.py`** - `DocstringChecker()` class with AST parsing and validation logic
- **`config.py`** - Configuration loading and `SectionConfig()` management
- **`cli.py`** - Typer-based CLI with dual entry points
- **`utils/exceptions.py`** - Custom exception classes for structured error handling


### 🤝 Contribution

Check the [CONTRIBUTING.md][github-contributing] file or [Contributing][docs-contributing] page.


### 🛠️ Development

1. **Clone the repository:**

    ```sh
    git clone https://github.com/data-science-extensions/docstring-format-checker.git
    cd docstring-format-checker
    ```

2. **Set up development environment:**

    ```sh
    uv sync --all-groups
    ```

3. **Run tests:**

    ```sh
    uv run pytest --config-file=pyproject.toml --cov-report=term-missing
    ```

4. **Run CLI locally:**

    ```sh
    uv run dfc --check examples/example_code.py
    ```


### 🧪 Build and Test

To ensure that the package works as expected, ensure that:

1. Write code in accordance with [PEP8][pep8] requirements.
2. Write a [UnitTest][unittest] for each function or feature included.
3. Maintain [CodeCoverage][codecov] at 100%.
4. Ensure all [UnitTests][pytest] pass.
5. Ensure [MyPy][mypy] passes 100%.


#### Testing

- Run them all together:

    ```sh
    uv run pytest --config-file=pyproject.toml
    ```

- Or run them individually:

    - **Tests with Coverage:**
        ```sh
        uv run pytest --config-file=pyproject.toml --cov-report=term-missing
        ```

    - **Type Checking:**
        ```sh
        uv run mypy src/
        ```

    - **Code Formatting:**
        ```sh
        uv run black --check src/
        ```

    - **Linting:**
        ```sh
        uv run ruff check src/
        ```


### 📄 License

This project is licensed under the MIT License - see the [LICENSE][github-license] file for details.

[github-repo]: https://github.com/data-science-extensions/docstring-format-checker
[github-contributing]: https://github.com/data-science-extensions/docstring-format-checker/blob/main/CONTRIBUTING.md
[docs-contributing]: https://data-science-extensions.com/docstring-format-checker/latest/usage/contributing/
[github-release]: https://github.com/data-science-extensions/docstring-format-checker/releases
[github-ci]: https://github.com/data-science-extensions/docstring-format-checker/actions/workflows/ci.yml
[github-cd]: https://github.com/data-science-extensions/docstring-format-checker/actions/workflows/cd.yml
[github-license]: https://github.com/data-science-extensions/docstring-format-checker/blob/main/LICENSE
[codecov-repo]: https://codecov.io/gh/data-science-extensions/docstring-format-checker
[pypi]: https://pypi.org/project/docstring-format-checker
[docs]: https://data-science-extensions.com/docstring-format-checker
[pip]: https://pypi.org/project/pip
[pipenv]: https://github.com/pypa/pipenv
[poetry]: https://python-poetry.org
[uv]: https://docs.astral.sh/uv/
[pep8]: https://peps.python.org/pep-0008/
[unittest]: https://docs.python.org/3/library/unittest.html
[codecov]: https://codecov.io/
[pytest]: https://docs.pytest.org
[mypy]: http://www.mypy-lang.org/
[black]: https://black.readthedocs.io/
