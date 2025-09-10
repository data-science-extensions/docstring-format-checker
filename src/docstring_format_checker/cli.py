# ============================================================================ #
#                                                                              #
#     Title: Title                                                             #
#     Purpose: Purpose                                                         #
#     Notes: Notes                                                             #
#     Author: chrimaho                                                         #
#     Created: Created                                                         #
#     References: References                                                   #
#     Sources: Sources                                                         #
#     Edited: Edited                                                           #
#                                                                              #
# ============================================================================ #


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Overview                                                              ####
#                                                                              #
# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
#  Description                                                              ####
# ---------------------------------------------------------------------------- #


"""
!!! note "Summary"
    Command-line interface for the docstring format checker.
"""


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Setup                                                                 ####
#                                                                              #
# ---------------------------------------------------------------------------- #


## --------------------------------------------------------------------------- #
##  Imports                                                                 ####
## --------------------------------------------------------------------------- #


# ## Python StdLib Imports ----
from functools import partial
from pathlib import Path
from textwrap import dedent
from typing import Optional

# ## Python Third Party Imports ----
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typer import Argument, CallbackParam, Context, Exit, Option, Typer, echo

# ## Local First Party Imports ----
from docstring_format_checker import __version__
from docstring_format_checker.config import (
    Config,
    find_config_file,
    load_config,
)
from docstring_format_checker.core import DocstringChecker, DocstringError


## --------------------------------------------------------------------------- #
##  Exports                                                                 ####
## --------------------------------------------------------------------------- #


__all__: list[str] = [
    "main",
    "entry_point",
]


## --------------------------------------------------------------------------- #
##  Constants                                                               ####
## --------------------------------------------------------------------------- #


NEW_LINE = "\n"


## --------------------------------------------------------------------------- #
##  Helpers                                                                 ####
## --------------------------------------------------------------------------- #


### Colours ----
def _colour(text: str, colour: str) -> str:
    return f"[{colour}]{text}[/{colour}]"


_green = partial(_colour, colour="green")
_red = partial(_colour, colour="red")
_cyan = partial(_colour, colour="cyan")
_blue = partial(_colour, colour="blue")


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Main Application                                                      ####
#                                                                              #
# ---------------------------------------------------------------------------- #


app = Typer(
    name="docstring-format-checker",
    help="A CLI tool to check and validate Python docstring formatting and completeness.",
    add_completion=False,
    rich_markup_mode="rich",
    add_help_option=False,  # Disable automatic help so we can add our own with -h
)
console = Console()


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Callbacks                                                             ####
#                                                                              #
# ---------------------------------------------------------------------------- #


def _version_callback(ctx: Context, param: CallbackParam, value: bool) -> None:
    """
    !!! note "Summary"
        Print version and exit.

    Params:
        ctx (Context):
            The context object.
        param (CallbackParam):
            The parameter object.
        value (bool):
            The boolean value indicating if the flag was set.

    Returns:
        (None):
            Nothing is returned.
    """
    if value:
        echo(f"docstring-format-checker version {__version__}")
        raise Exit()


def _help_callback_main(ctx: Context, param: CallbackParam, value: bool) -> None:
    """
    !!! note "Summary"
        Show help and exit.

    Params:
        ctx (Context):
            The context object.
        param (CallbackParam):
            The parameter object.
        value (bool):
            The boolean value indicating if the flag was set.

    Returns:
        (None):
            Nothing is returned.
    """
    if not value or ctx.resilient_parsing:
        return
    echo(ctx.get_help())
    raise Exit()


def _example_callback(ctx: Context, param: CallbackParam, value: Optional[str]) -> None:
    """
    !!! note "Summary"
        Handle example flag and show appropriate example content.

    Params:
        ctx (Context):
            The context object.
        param (CallbackParam):
            The parameter object.
        value (Optional[str]):
            The example type to show: 'config' or 'usage'.

    Returns:
        (None):
            Nothing is returned.
    """

    if not value or ctx.resilient_parsing:
        return

    if value == "config":
        _show_config_example_callback()
    elif value == "usage":
        _show_usage_examples_callback()
    else:
        console.print(_red(f"Error: Invalid example type '{value}'. Use 'config' or 'usage'."))
        raise Exit(1)


def _show_usage_examples_callback() -> None:
    """
    !!! note "Summary"
        Show examples and exit.

    Params:
        ctx (Context):
            The context object.
        param (CallbackParam):
            The parameter object.
        value (bool):
            The boolean value indicating if the flag was set.

    Returns:
        (None):
            Nothing is returned.
    """

    examples_content: str = dedent(
        f"""
        {_green("dfc myfile.py")}                   Check a single Python file (list output)
        {_green("dfc src/")}                        Check all Python files in src/ directory
        {_green("dfc --output=table myfile.py")}    Check with table output format
        {_green("dfc -o list myfile.py")}           Check with list output format (default)
        {_green("dfc --check myfile.py")}           Check and exit with error if issues found
        {_green("dfc --quiet myfile.py")}           Check quietly, only show pass/fail
        {_green("dfc --quiet --check myfile.py")}   Check quietly and exit with error if issues found
        {_green("dfc . --exclude '*/tests/*'")}     Check current directory, excluding tests
        {_green("dfc . -c custom.toml")}            Use custom configuration file
        {_green("dfc --example=config")}            Show example configuration
        {_green("dfc -e usage")}                    Show usage examples (this help)
        """
    ).strip()

    panel = Panel(
        examples_content,
        title="Examples",
        title_align="left",
        border_style="dim",
        padding=(0, 1),
    )

    console.print(panel)
    raise Exit()


def _show_config_example_callback() -> None:
    """
    !!! note "Summary"
        Show configuration example and exit.

    Params:
        ctx (Context):
            The context object.
        param (CallbackParam):
            The parameter object.
        value (bool):
            The boolean value indicating if the flag was set.

    Returns:
        (None):
            Nothing is returned.
    """

    example_config: str = dedent(
        """
        # Example configuration for docstring-format-checker
        # Place this in your pyproject.toml file

        [tool.dfc]
        # or [tool.docstring-format-checker]

        [[tool.dfc.sections]]
        order = 1
        name = "summary"
        type = "free_text"
        admonition = "note"
        prefix = "!!!"
        required = true

        [[tool.dfc.sections]]
        order = 2
        name = "details"
        type = "free_text"
        admonition = "info"
        prefix = "???+"
        required = false

        [[tool.dfc.sections]]
        order = 3
        name = "params"
        type = "list_name_and_type"
        required = true

        [[tool.dfc.sections]]
        order = 4
        name = "returns"
        type = "list_name_and_type"
        required = false

        [[tool.dfc.sections]]
        order = 5
        name = "yields"
        type = "list_type"
        required = false

        [[tool.dfc.sections]]
        order = 6
        name = "raises"
        type = "list_type"
        required = false

        [[tool.dfc.sections]]
        order = 7
        name = "examples"
        type = "free_text"
        admonition = "example"
        prefix = "???+"
        required = false

        [[tool.dfc.sections]]
        order = 8
        name = "notes"
        type = "free_text"
        admonition = "note"
        prefix = "???"
        required = false
        """
    ).strip()

    # Print without Rich markup processing to avoid bracket interpretation
    console.print(example_config, markup=False)
    raise Exit()


def _format_error_messages(error_message: str) -> str:
    """
    !!! note "Summary"
        Format error messages for better readability in CLI output.

    Params:
        error_message (str):
            The raw error message that may contain semicolon-separated errors

    Returns:
        (str):
            Formatted error message with each error prefixed with "- " and separated by ";\n"
    """
    if "; " in error_message:
        # Split by semicolon and rejoin with proper formatting
        errors: list[str] = error_message.split("; ")
        formatted_errors: list[str] = [f"- {error.strip()}" for error in errors if error.strip()]
        return ";\n".join(formatted_errors) + "."
    else:
        # Single error message
        return f"- {error_message.strip()}."


def _display_results(results: dict[str, list[DocstringError]], quiet: bool, output: str, check: bool) -> int:
    """
    !!! note "Summary"
        Display the results of docstring checking.

    Params:
        results (dict[str, list[DocstringError]]):
            Dictionary mapping file paths to lists of errors
        quiet (bool):
            Whether to suppress success messages and error details
        output (str):
            Output format: 'table' or 'list'
        check (bool):
            Whether this is a check run (affects quiet behavior)

    Returns:
        (int):
            Exit code (`0` for success, `1` for errors found)
    """
    if not results:
        if not quiet:
            console.print(_green("✓ All docstrings are valid!"))
        return 0

    # Count total errors (individual error messages, not error objects)
    total_individual_errors: int = 0
    total_functions: int = 0

    for errors in results.values():
        total_functions += len(errors)  # Count functions/items with errors
        for error in errors:
            # Count individual error messages within each error object
            if "; " in error.message:
                individual_errors = [msg.strip() for msg in error.message.split("; ") if msg.strip()]
                total_individual_errors += len(individual_errors)
            else:
                total_individual_errors += 1

    total_errors: int = total_individual_errors
    total_files: int = len(results)

    if quiet:
        # In quiet mode, only show summary with improved format
        if total_functions == 1:
            functions_text = f"1 function"
        else:
            functions_text = f"{total_functions} functions"

        if total_files == 1:
            files_text = f"1 file"
        else:
            files_text = f"{total_files} files"

        console.print(_red(f"{NEW_LINE}Found {total_errors} error(s) in {functions_text} over {files_text}"))
        return 1

    if output == "table":
        # Show detailed table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("File", style="cyan", no_wrap=False)
        table.add_column("Line", justify="right", style="white")
        table.add_column("Item", style="yellow")
        table.add_column("Type", style="blue")
        table.add_column("Error", style="red")

        for file_path, errors in results.items():
            for i, error in enumerate(errors):
                file_display: str = file_path if i == 0 else ""

                # Format error message with improved formatting
                formatted_error_message: str = _format_error_messages(error.message)

                table.add_row(
                    file_display,
                    str(error.line_number) if error.line_number > 0 else "",
                    error.item_name,
                    error.item_type,
                    formatted_error_message,
                )
        console.print(table)

    else:
        # Show compact output with grouped errors under function/class headers
        for file_path, errors in results.items():
            console.print(f"{NEW_LINE}{_cyan(file_path)}")
            for error in errors:
                # Print the header line with line number, item type and name
                if error.line_number > 0:
                    console.print(f"  [red]Line {error.line_number}[/red] - {error.item_type} '{error.item_name}':")
                else:
                    console.print(f"  {_red('Error')} - {error.item_type} '{error.item_name}':")

                # Split error message into individual errors and indent them
                if "; " in error.message:
                    individual_errors = [msg.strip() for msg in error.message.split("; ") if msg.strip()]
                    for individual_error in individual_errors:
                        console.print(f"    - {individual_error}")
                else:
                    # Single error message
                    console.print(f"    - {error.message.strip()}")

    # Summary - more descriptive message
    if total_functions == 1:
        functions_text = f"1 function"
    else:
        functions_text = f"{total_functions} functions"

    if total_files == 1:
        files_text = f"1 file"
    else:
        files_text = f"{total_files} files"

    console.print(_red(f"{NEW_LINE}Found {total_errors} error(s) in {functions_text} over {files_text}"))

    return 1


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Main Logic                                                            ####
#                                                                              #
# ---------------------------------------------------------------------------- #


# This will be the default behavior when no command is specified
def check_docstrings(
    path: str,
    config: Optional[str] = None,
    exclude: Optional[list[str]] = None,
    quiet: bool = False,
    output: str = "list",
    check: bool = False,
) -> None:
    """
    !!! note "Summary"
        Core logic for checking docstrings.

    Params:
        path (str):
            The path to the file or directory to check.
        config (Optional[str]):
            The path to the configuration file.
            Default: `None`.
        exclude (Optional[list[str]]):
            List of glob patterns to exclude from checking.
            Default: `None`.
        quiet (bool):
            Whether to suppress output.
            Default: `False`.
        output (str):
            Output format: 'table' or 'list'.
            Default: `'list'`.
        check (bool):
            Whether to throw error if issues are found.
            Default: `False`.

    Returns:
        (None):
            Nothing is returned.
    """

    target_path = Path(path)

    # Validate target path
    if not target_path.exists():
        console.print(_red(f"Error: Path does not exist: '{path}'"))
        raise Exit(1)

    # Load configuration
    try:
        if config:
            config_path = Path(config)
            if not config_path.exists():
                console.print(_red(f"Error: Configuration file does not exist: {config}"))
                raise Exit(1)
            config_obj = load_config(config_path)
        else:
            # Try to find config file automatically
            found_config: Optional[Path] = find_config_file(target_path if target_path.is_dir() else target_path.parent)
            if found_config:
                config_obj: Config = load_config(found_config)
            else:
                config_obj: Config = load_config()

    except Exception as e:
        console.print(_red(f"Error loading configuration: {e}"))
        raise Exit(1)

    # Initialize checker
    checker = DocstringChecker(config_obj)

    # Check files
    try:
        if target_path.is_file():
            errors: list[DocstringError] = checker.check_file(target_path)
            results: dict[str, list[DocstringError]] = {str(target_path): errors} if errors else {}
        else:
            results: dict[str, list[DocstringError]] = checker.check_directory(target_path, exclude_patterns=exclude)
    except Exception as e:
        console.print(_red(f"Error during checking: {e}"))
        raise Exit(1)

    # Display results
    exit_code: int = _display_results(results, quiet, output, check)

    # Always exit with error code if issues are found, regardless of check flag
    if exit_code != 0:
        raise Exit(exit_code)


# ---------------------------------------------------------------------------- #
#                                                                              #
#     App Operators                                                         ####
#                                                                              #
# ---------------------------------------------------------------------------- #


# Simple callback that only handles global options and delegates to subcommands
@app.callback(invoke_without_command=True)
def main(
    ctx: Context,
    path: Optional[str] = Argument(None, help="Path to Python file or directory to check"),
    config: Optional[str] = Option(None, "--config", "-f", help="Path to configuration file (TOML format)"),
    exclude: Optional[list[str]] = Option(
        None,
        "--exclude",
        "-x",
        help="Glob patterns to exclude (can be used multiple times)",
    ),
    output: str = Option(
        "list",
        "--output",
        "-o",
        help="Output format: 'table' or 'list'",
        show_default=True,
    ),
    check: bool = Option(
        False,
        "--check",
        "-c",
        help="Throw error (exit 1) if any issues are found",
    ),
    quiet: bool = Option(
        False,
        "--quiet",
        "-q",
        help="Only output pass/fail confirmation, suppress errors unless failing",
    ),
    example: Optional[str] = Option(
        None,
        "--example",
        "-e",
        callback=_example_callback,
        is_eager=True,
        help="Show examples: 'config' for configuration example, 'usage' for usage examples",
    ),
    version: Optional[bool] = Option(
        None,
        "--version",
        "-v",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
    help_flag: Optional[bool] = Option(
        None,
        "--help",
        "-h",
        callback=_help_callback_main,
        is_eager=True,
        help="Show this message and exit",
    ),
) -> None:
    """
    !!! note "Summary"
        Check Python docstring formatting and completeness.

    ???+ abstract "Details"
        This tool analyzes Python files and validates that functions, methods, and classes have properly formatted docstrings according to the configured sections.

    Params:
        ctx (Context):
            The context object for the command.
        path (Optional[str]):
            Path to Python file or directory to check.
        config (Optional[str]):
            Path to configuration file (TOML format).
        exclude (Optional[list[str]]):
            Glob patterns to exclude.
        output (str):
            Output format: 'table' or 'list'.
        check (bool):
            Throw error if any issues are found.
        quiet (bool):
            Only output pass/fail confirmation.
        example (Optional[str]):
            Show examples: 'config' or 'usage'.
        version (Optional[bool]):
            Show version and exit.
        help_flag (Optional[bool]):
            Show help message and exit.

    Returns:
        (None):
            Nothing is returned.
    """

    # If no path is provided, show help
    if path is None:
        echo(ctx.get_help())
        raise Exit(0)

    # Validate output format
    if output not in ["table", "list"]:
        console.print(_red(f"Error: Invalid output format '{output}'. Use 'table' or 'list'."))
        raise Exit(1)

    check_docstrings(
        path=path,
        config=config,
        exclude=exclude,
        quiet=quiet,
        output=output,
        check=check,
    )


def entry_point() -> None:
    """
    !!! note "Summary"
        Entry point for the CLI scripts defined in pyproject.toml.
    """
    app()


if __name__ == "__main__":
    app()
