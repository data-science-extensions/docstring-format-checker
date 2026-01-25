# Getting Started with `docstring-format-checker`

Welcome to `docstring-format-checker` (or `dfc` for short)! Utilise this guide to help you get up and run with the tool, from installation to advanced configuration. Target developers who are new to Python or those who want to standardise their project's documentation.


## 📥 Installation

First, install the package using your preferred package manager. Use `uv` for its speed and reliability, but `pip`, `poetry`, and `pipenv` are all supported.


### Install using `uv`

Execute the following command in your terminal:

```sh {.sh .bash linenums="1" title="Terminal"}
uv add docstring-format-checker
```


### Install using `pip`

Alternatively, use the standard Python package manager:

```sh {.sh .bash linenums="1" title="Terminal"}
pip install docstring-format-checker
```


## 🚀 Your First Check

Walk through a simple example to see how `dfc` work.


### Create a sample module

Create a new file named `sample.py` with the following content. Include a function with a docstring that misses some common sections like a summary and standardised parameter names.

```python {.py .python linenums="1" title="sample.py"}
--8<-- "docs/usage/examples/sample_bad.py"
```


### Run the tool

Now, run `dfc` against your new file:

```sh {.sh .bash linenums="1" title="Terminal"}
dfc --check sample.py
```

<div class="result" markdown>

`dfc` notify you that the docstring fail to meet the default standards:

```text
  Line 1 - function 'calculate_area':
    - Missing required section: 'summary'
    - Missing required section: 'params'
    - Section 'args' found in docstring but not defined in configuration
  Line 15 - function 'calculate_perimeter':
    - Missing required section: 'summary'
    - Missing required section: 'params'
    - Section 'parameters' found in docstring but not defined in configuration

Found 6 error(s) in 2 functions over 1 file
```

</div>

By default, `dfc` expects a summary formatted as an admonition (like `!!! note "Summary"`) and a section named `Params` instead of `Args`.


### Get help

If you ever feel unsure about the available commands or options, use the `--help` (or `-h`) flag:

```sh {.sh .bash linenums="1" title="Terminal"}
dfc --help
```

<div class="result" markdown>

This displays the help message, which includes usage examples and a configuration template:

```text
     _                _        _                    __                            _             _               _
  __| | ___   ___ ___| |_ _ __(_)_ __   __ _       / _| ___  _ __ _ __ ___   __ _| |_       ___| |__   ___  ___| | _____ _ __
 / _` |/ _ \ / __/ __| __| '__| | '_ \ / _` |_____| |_ / _ \| '__| '_ ` _ \ / _` | __|____ / __| '_ \ / _ \/ __| |/ / _ \ '__|
| (_| | (_) | (__\__ \ |_| |  | | | | | (_| |_____|  _| (_) | |  | | | | | | (_| | ||_____| (__| | | |  __/ (__|   <  __/ |
 \__,_|\___/ \___|___/\__|_|  |_|_| |_|\__, |     |_|  \___/|_|  |_| |_| |_|\__,_|\__|     \___|_| |_|\___|\___|_|\_\___|_|
                                       |___/


 Usage: dfc [OPTIONS] [PATHS]... COMMAND [ARGS]...

 A CLI tool to check and validate Python docstring formatting and completeness.

╭─ Arguments ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│   paths      [PATHS]...  Path(s) to Python file(s) or directory(s) for DFC to check                                                                                               │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --config   -f      TEXT  Path to configuration file (TOML format)                                                                                                                 │
│ --exclude  -x      TEXT  Glob patterns to exclude (can be used multiple times)                                                                                                    │
│ --output   -o      TEXT  Output format: 'table' or 'list' [default: list]                                                                                                         │
│ --check    -c            Throw error (exit 1) if any issues are found                                                                                                             │
│ --quiet    -q            Only output pass/fail confirmation, suppress errors unless failing                                                                                       │
│ --example  -e      TEXT  Show examples: 'config' for configuration example, 'usage' for usage examples                                                                            │
│ --version  -v            Show version and exit                                                                                                                                    │
│ --help     -h            Show this message and exit                                                                                                                               │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭─ Usage Examples ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Execute the below commands in any terminal after installing the package.                                                                                                          │
│                                                                                                                                                                                   │
│ dfc myfile.py                   # Check a single Python file (list output)                                                                                                        │
│ dfc myfile.py other_file.py     # Check multiple Python files                                                                                                                     │
│ dfc src/                        # Check all Python files in src/ directory                                                                                                        │
│ dfc -x src/app/__init__.py src/ # Check all Python files in src/ directory, excluding one init file                                                                               │
│ dfc --output=table myfile.py    # Check with table output format                                                                                                                  │
│ dfc -o list myfile.py           # Check with list output format (default)                                                                                                         │
│ dfc --check myfile.py           # Check and exit with error if issues found                                                                                                       │
│ dfc --quiet myfile.py           # Check quietly, only show pass/fail                                                                                                              │
│ dfc --quiet --check myfile.py   # Check quietly and exit with error if issues found                                                                                               │
│ dfc . --exclude '*/tests/*'     # Check current directory, excluding tests                                                                                                        │
│ dfc . -c custom.toml            # Use custom configuration file                                                                                                                   │
│ dfc --example=config            # Show example configuration                                                                                                                      │
│ dfc -e usage                    # Show usage examples (this help)                                                                                                                 │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Configuration Example ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Place the below config in your `pyproject.toml` file.                                                                                                                             │
│                                                                                                                                                                                   │
│ [tool.dfc]                                                                                                                                                                        │
│ # or [tool.docstring-format-checker]                                                                                                                                              │
│ allow_undefined_sections = false                                                                                                                                                  │
│ require_docstrings = true                                                                                                                                                         │
│ check_private = true                                                                                                                                                              │
│ validate_param_types = true                                                                                                                                                       │
│ optional_style = "validate"  # "silent", "validate", or "strict"                                                                                                                  │
│ sections = [                                                                                                                                                                      │
│     { order = 1, name = "summary",  type = "free_text",          required = true, admonition = "note", prefix = "!!!" },                                                          │
│     { order = 2, name = "details",  type = "free_text",          required = false, admonition = "abstract", prefix = "???+" },                                                    │
│     { order = 3, name = "params",   type = "list_name_and_type", required = false },                                                                                              │
│     { order = 4, name = "raises",   type = "list_type",          required = false },                                                                                              │
│     { order = 5, name = "returns",  type = "list_name_and_type", required = false },                                                                                              │
│     { order = 6, name = "yields",   type = "list_type",          required = false },                                                                                              │
│     { order = 7, name = "examples", type = "free_text",          required = false, admonition = "example", prefix = "???+" },                                                     │
│     { order = 8, name = "notes",    type = "free_text",          required = false, admonition = "note", prefix = "???" },                                                         │
│ ]                                                                                                                                                                                 │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

</div>


## 🛠️ Configuring `dfc`

To get the most out of `dfc`, define your documentation standards in a `pyproject.toml` file. Use this standard configuration file for Python projects.


### Create a configuration file

Create a `pyproject.toml` file in your root directory (or update your existing one) with the following content. Specify the section names you prefer:

```toml {.toml linenums="1" title="pyproject.toml"}
--8<-- "docs/usage/examples/pyproject.toml"
```


### Understand the options

In the above sample, we have provided three global options and three sections which contain 4 or more attributes each:

- `require_docstrings`: When set to `true`, `dfc` report an error for any public function, method, or class that lack a docstring.
- `validate_param_types`: Ensure that parameters in the docstring include type annotations (e.g., `width (int): ...`).
- `sections`: This list define the specific parts of a docstring that `dfc` should look for and validate. Each section have a `name`, `type`, and can be `required`.

However, there are more options available to fine-tune the behaviour of `dfc`. The Global section allows five different options, and each section has the possibility of seven options. Here is a brief overview of some commonly used options:

- Global:
    - `allow_undefined_sections`: When set to `false`, `dfc` report an error if the docstring contains sections that are not defined in the configuration.
    - `require_docstrings`: When set to `true`, `dfc` report an error for any public function, method, or class that lack a docstring.
    - `check_private`: When set to `true`, `dfc` also check private functions, methods, and classes (those prefixed with an underscore).
    - `validate_param_types`: Ensure that parameters in the docstring include type annotations (e.g., `width (int): ...`).
    - `optional_style`: Defines how optional sections are treated. Options include `silent`, `validate`, and `strict`.
- Section:
    - `name`: The name of the section as it should appear in the docstring.
    - `type`: The type of content expected in the section (e.g., `free_text`, `list_name_and_type`, `list_type`).
    - `order`: The order in which the section should appear in the docstring.
    - `admonition`: The type of admonition to use for the section (e.g., `note`, `abstract`, `example`).
    - `prefix`: The prefix used to denote the section in the docstring (e.g., `!!!`, `???+`, `???`).
    - `required`: Whether the section is mandatory (`true`) or optional (`false`).
    - `message`: A custom error message to display if the section is missing or incorrectly formatted.

Refer to the [Configuration](../usage/configuration.md) page for a full list of available options and their descriptions.


### Run the tool again

Now that you have a configuration, run `dfc` on `sample.py` again:

```sh {.sh .bash linenums="1" title="Terminal"}
dfc --check sample.py
```

<div class="result" markdown>

Expected output:

```text
  Line 1 - function 'calculate_area':
    - Missing required section: 'summary'
    - Missing required section: 'params'
    - Section 'args' found in docstring but not defined in configuration
  Line 15 - function 'calculate_perimeter':
    - Missing required section: 'summary'
    - Missing required section: 'params'
    - Section 'parameters' found in docstring but not defined in configuration

Found 6 error(s) in 2 functions over 1 file
```

</div>

`dfc` notify you that the `summary` section is missing (because it expect a `Summary:` header), and the `params` section fail to match the docstring's `Args:` header.


### Fix the docstring

Update `calculate_area()` in `sample.py` to match the required format. Ensure you include type annotations in the signature and parenthesised types in the docstring:

```python {.py .python linenums="1" title="sample.py"}
--8 < --"docs/usage/examples/sample_good.py"
```

Now run the check again:

```sh {.sh .bash linenums="1" title="Terminal"}
dfc --check sample.py
```

<div class="result" markdown>

```text
✅ All docstrings are valid!
```

</div>


## 💡 Troubleshooting and Watch-outs

As you begin use `dfc`, keep these points in mind to ensure a smooth experience.


### **Watch-out**: Order matters

If you define an `order` for your sections in `pyproject.toml`, `dfc` enforce that specific order. If a `returns` section appear before a `params` section but the config say otherwise, `dfc` raise an error.


### **Pro-tip**: Floating sections

Omit the `order` attribute for sections like "Deprecation Warning" or "Notes" that might appear anywhere in the docstring. Call these sections "floating" sections.


### **Common Pitfall**: Indentation

`dfc` use AST parsing to understand your code, but it still expect standard Python indentation. Always correctly indent your docstrings relative to the function or class they describe.


## 🛤️ Next Steps

Now that you have the basics down, explore the [Configuration](../usage/configuration.md) page for a full list of available options and section types. Integrate `dfc` into your CI/CD pipeline or use it as a pre-commit hook to automate your documentation checks.
