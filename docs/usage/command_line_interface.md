# CLI Interaction Guide


Interface directly with the `docstring-format-checker` (or `dfc`) to standardise your project's documentation. Access a detailed walkthrough of all command-line operations, designed to help new developers master the tool's capabilities.


## 🛠️ The `dfc` Command

Interact with the tool primarily through the `dfc` command. Treat this as an alias for the longer `docstring-format-checker` command, providing a more concise interface for frequent use.


### 📟 Basic Syntax

Follow the general structure of a `dfc` command:

```sh {.sh .bash title="Terminal"}
dfc [OPTIONS] [PATHS]...
```

Target one or more paths, such as specific Python files or entire directories.


### Full Help Command (`--help` / `-h`)

```sh {.sh .bash title="Terminal"}
dfc --help
```

<div class="result" markdown>

```txt
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


## 📂 Target Paths

Determine which parts of your codebase `dfc` should examine.


### 📄 Single Files

Check an individual file by providing its path:

```sh {.sh .bash title="Terminal"}
dfc sample.py
```


### 📁 Directories

Check all Python files within a directory (including subdirectories) by providing the folder path:

```sh {.sh .bash title="Terminal"}
dfc src/
```


### 🗃️ Multiple Targets

Combine multiple files and directories in a single command:

```sh {.sh .bash title="Terminal"}
dfc module1.py src/utils/
```


## ⚙️ Core Options

Customise the behaviour of `dfc` and its search location for settings.


### 📄 Configuration File (`--config` / `-f`)

Direct `dfc` to look for a `[tool.dfc]` section in your [pyproject.toml](examples/pyproject.toml). Use this option to point to a specific TOML file instead.

```sh {.sh .bash title="Terminal"}
dfc --config=custom_config.toml src/
```


### 🚫 Exclusion Patterns (`--exclude` / `-x`)

Ignore specific files or directories using glob patterns. This is particularly useful for skipping third-party libraries, virtual environments, or test suites.

```sh {.sh .bash title="Terminal"}
dfc . --exclude='*/tests/*' --exclude 'setup.py'
```

!!! tip "Note"
    Provide the `--exclude` flag multiple times to specify several patterns.


### 🎨 Output Format (`--output` / `-o`)

Standardise the appearance of error reports. Choose between a detailed `list` (default) or a structured `table`.


#### 📝 Render as a list

```sh {.sh .bash title="Terminal"}
dfc --output=list sample.py
```

<div class="result" markdown>

```text
sample.py
  Line 1 - function 'calculate_area':
    - Missing required section: 'summary'
    - Missing required section: 'params'
```

</div>


#### 📊 Render as a table

```sh {.sh .bash title="Terminal"}
dfc --output=table sample.py
```

<div class="result" markdown>

```text
┏━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ File      ┃ Line ┃ Item           ┃ Type     ┃ Error                                 ┃
┡━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ sample.py │    1 │ calculate_area │ function │ - Missing required section: 'summary' │
└───────────┴──────┴────────────────┴──────────┴───────────────────────────────────────┘
```

</div>


## 🛡️ Execution Controls

Manage the interaction between `dfc` and other tools or scripts.


### 🏁 Check Mode (`--check` / `-c`)

Ensure that `dfc` return a non-zero exit code if any issues are found. Integrate `dfc` into Continuous Integration (CI) pipelines or git hooks with this flag.


```sh {.sh .bash title="Terminal"}
dfc --check src/
```


### 🔇 Quiet Mode (`--quiet` / `-q`)

Suppress all detailed error messages. Report only a high-level summary if errors occur, or nothing at all if the check pass.

```sh {.sh .bash title="Terminal"}
dfc --quiet --check src/
```


## 📖 Helper Commands

Access built-in documentation and version information directly from the terminal.


### 💡 Show Examples (`--example` / `-e`)

View pre-configured templates to help you get started quickly.

- `--example config`: Display a comprehensive TOML configuration template.
- `--example usage`: Display common CLI usage patterns.

```sh {.sh .bash title="Terminal"}
dfc --example=config
```


### 🔢 Version Information (`--version` / `-v`)

Check which version of `docstring-format-checker` is currently installed.

```sh {.sh .bash title="Terminal"}
dfc --version
```


### ❓ Help Message (`--help` / `-h`)

Display a full summary of all available arguments, options, and usage examples.

```sh {.sh .bash title="Terminal"}
dfc --help
```


## 🎓 Guided Walkthrough

Follow these steps to explore the most important features of the `dfc` CLI.


### 🏗️ 1. Create a workspace

Prepare a small environment with a few sample files to test the tool. Create a directory named `dfc_walkthrough` and add the following files:


```python {.py .python title="dfc_walkthrough/good_code.py"}
--8<--"docs/usage/examples/sample_good.py"
```


```python {.py .python title="dfc_walkthrough/bad_code.py"}
--8<--"docs/usage/examples/sample_bad.py"
```


### 🔍 2. Identify issues

Run a standard check on the `bad_code.py` file to see the inconsistency reports from `dfc`.


```sh {.sh .bash title="Terminal"}
dfc bad_code.py
```


Expect `dfc` to identify missing summary admonitions and incorrectly named sections like `Args` (which should be `Params` by default).


### 📊 3. Utilise the table view

Switch to the table format to get a more structured overview of the errors. Read multiple issues with ease using this layout.

```sh {.sh .bash title="Terminal"}
dfc --output=table bad_code.py
```


### 📂 4. Check an entire directory

Instruct `dfc` to scan the whole directory. Find all `.py` files and report on each one automatically.


```sh {.sh .bash title="Terminal"}
dfc .
```


View results for both `good_code.py` (which should pass) and `bad_code.py` in the output.


### 🤖 5. Standardise for CI

Prepare your commands for a CI environment. Use the `--quiet` and `--check` flags to ensure that the process fail if documentation is insufficient, without cluttering the logs.

```sh {.sh .bash title="Terminal"}
dfc --quiet --check .
```

<div class="result" markdown>

Observe no output upon a successful check. Receive a concise summary if errors are present:

```text
Found 6 error(s) in 2 functions over 1 file
```

</div>


## ⚠️ Watch Out

Keep these nuances in mind to avoid common pitfalls:


### 🐚 Shell Pattern Matching

Different shells (like `bash`, `zsh`, or `fish`) handle glob patterns (like `*`) differently. Always surround your exclusion patterns with quotes to ensure they are passed correctly to `dfc`.

- **Correct**: `dfc --exclude '*/tests/*' .`
- **Incorrect**: `dfc --exclude */tests/* .`


### 📝 Argument Order

Move flags to the start of the command if errors occur (a common requirement for `Typer`-based tools):

- **Recommended**: `dfc --output=table src/`
- **Sometimes Unreliable**: `dfc src/ --output=table`
