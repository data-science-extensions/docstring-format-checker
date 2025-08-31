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
from pathlib import Path
from textwrap import dedent
from typing import Optional

# ## Python Third Party Imports ----
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from toolbox_python.bools import strtobool
from typer import (
    Argument,
    BadParameter,
    CallbackParam,
    Context,
    Exit,
    Option,
    Typer,
    echo,
)

# ## Local First Party Imports ----
from docstring_format_checker import __version__
from docstring_format_checker.config import SectionConfig, find_config_file, load_config
from docstring_format_checker.core import DocstringChecker, DocstringError


## --------------------------------------------------------------------------- #
##  Exports                                                                 ####
## --------------------------------------------------------------------------- #


__all__: list[str] = [
    "main",
    "config_example",
    "check",
    "entry_point",
]


## --------------------------------------------------------------------------- #
##  Constants                                                               ####
## --------------------------------------------------------------------------- #


NEW_LINE = "\n"


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
    Print version and exit.
    """
    if value:
        echo(f"docstring-format-checker version {__version__}")
        raise Exit()


def _help_callback(ctx: Context, param: CallbackParam, value: bool) -> None:
    """
    Show help and exit.
    """
    if not value or ctx.resilient_parsing:
        return
    echo(ctx.get_help())
    raise Exit()


def _parse_boolean_flag(ctx: Context, param: CallbackParam, value: Optional[str]) -> Optional[bool]:
    """
    Parse boolean flag that accepts various true/false values.
    """

    # Handle the case where the flag is provided without a value (e.g., just --recursive or -r)
    # In this case, Typer doesn't call the callback, so we need to handle it differently
    if value is None:
        # This means the flag wasn't provided at all, use default
        return True

    # If value is an empty string, it means the flag was provided without a value
    if value == "":
        return True

    try:
        return strtobool(value)
    except ValueError as e:
        raise BadParameter(
            message=(
                f"Invalid boolean value: '{value}'.{NEW_LINE}"
                "Use one of: true/false, t/f, yes/no, y/n, 1/0, or on/off."
            )
        ) from e


def _parse_recursive_flag(value: str) -> bool:
    """
    Parse recursive flag using strtobool utility.
    """
    return strtobool(value)


def _show_examples_callback(ctx: Context, param: CallbackParam, value: bool) -> None:
    """
    Show examples and exit.
    """

    if not value or ctx.resilient_parsing:
        return

    examples_content: str = dedent(
        """
        [green]dfc check myfile.py[/green]                    Check a single Python file
        [green]dfc check src/[/green]                         Check all Python files in src/ directory
        [green]dfc check . --exclude "*/tests/*"[/green]      Check current directory, excluding tests
        [green]dfc check . -c custom.toml[/green]             Use custom configuration file
        [green]dfc check . --verbose[/green]                  Show detailed validation output
        [green]dfc config-example[/green]                     Show example configuration
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


def _show_check_examples_callback(ctx: Context, param: CallbackParam, value: bool) -> None:
    """
    Show check command examples and exit.
    """

    if not value or ctx.resilient_parsing:
        return

    examples_content: str = dedent(
        """
        [green]dfc check myfile.py[/green]                    Check a single Python file
        [green]dfc check src/[/green]                         Check all Python files in src/ directory
        [green]dfc check . --exclude "*/tests/*"[/green]      Check current directory, excluding tests
        [green]dfc check . --config custom.toml[/green]       Use custom configuration file
        [green]dfc check . --verbose --recursive[/green]      Show detailed output for all subdirectories
        [green]dfc check . --quiet[/green]                    Only show errors, suppress success messages
        """
    )

    panel = Panel(
        examples_content,
        title="Check Command Examples",
        title_align="left",
        border_style="dim",
        padding=(0, 1),
    )

    console.print(panel)
    raise Exit()


def _display_results(results: dict[str, list[DocstringError]], quiet: bool, verbose: bool) -> int:
    """
    Display the results of docstring checking.

    Args:
        results:
            Dictionary mapping file paths to lists of errors
        quiet:
            Whether to suppress success messages
        verbose:
            Whether to show detailed output

    Returns:
        Exit code (0 for success, 1 for errors found)
    """
    if not results:
        if not quiet:
            console.print("[green]✓ All docstrings are valid![/green]")
        return 0

    # Count total errors
    total_errors: int = sum(len(errors) for errors in results.values())
    total_files: int = len(results)

    if verbose:
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
                table.add_row(
                    file_display,
                    str(error.line_number) if error.line_number > 0 else "",
                    error.item_name,
                    error.item_type,
                    error.message,
                )
        console.print(table)

    else:
        # Show compact output
        for file_path, errors in results.items():
            console.print(f"{NEW_LINE}[cyan]{file_path}[/cyan]")
            for error in errors:
                if error.line_number > 0:
                    console.print(
                        f"  [red]Line {error.line_number}[/red] - {error.item_type} '{error.item_name}': {error.message}"
                    )
                else:
                    console.print(f"  [red]Error[/red]: {error.message}")

    # Summary
    console.print(f"{NEW_LINE}[red]Found {total_errors} error(s) in {total_files} file(s)[/red]")

    return 1


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Main Logic                                                            ####
#                                                                              #
# ---------------------------------------------------------------------------- #


# This will be the default behavior when no command is specified
def _check_docstrings(
    path: str,
    config: Optional[str] = None,
    recursive: bool = True,
    exclude: Optional[list[str]] = None,
    quiet: bool = False,
    verbose: bool = False,
) -> None:
    """
    Core logic for checking docstrings.
    """

    target_path = Path(path)

    # Validate target path
    if not target_path.exists():
        console.print(f"[red]Error: Path does not exist: {path}[/red]")
        raise Exit(1)

    # Load configuration
    try:
        if config:
            config_path = Path(config)
            if not config_path.exists():
                console.print(f"[red]Error: Configuration file does not exist: {config}[/red]")
                raise Exit(1)
            sections_config = load_config(config_path)
        else:
            # Try to find config file automatically
            found_config: Path | None = find_config_file(target_path if target_path.is_dir() else target_path.parent)
            if found_config:
                if verbose:
                    console.print(f"[blue]Using configuration from: {found_config}[/blue]")
                sections_config: list[SectionConfig] = load_config(found_config)
            else:
                if verbose:
                    console.print("[blue]Using default configuration[/blue]")
                sections_config: list[SectionConfig] = load_config()

    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        raise Exit(1)

    # Initialize checker
    checker = DocstringChecker(sections_config)

    # Check files
    try:
        if target_path.is_file():
            if verbose:
                console.print(f"[blue]Checking file: {target_path}[/blue]")
            errors: list[DocstringError] = checker.check_file(target_path)
            results: dict[str, list[DocstringError]] = {str(target_path): errors} if errors else {}
        else:
            if verbose:
                console.print(f"[blue]Checking directory: {target_path} (recursive={recursive})[/blue]")
            results: dict[str, list[DocstringError]] = checker.check_directory(
                target_path, recursive=recursive, exclude_patterns=exclude
            )
    except Exception as e:
        console.print(f"[red]Error during checking: {e}[/red]")
        raise Exit(1)

    # Display results
    exit_code: int = _display_results(results, quiet, verbose)

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
    version: Optional[bool] = Option(
        None,
        "--version",
        "-v",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
    examples: Optional[bool] = Option(
        None,
        "--examples",
        "-e",
        callback=_show_examples_callback,
        is_eager=True,
        help="Show usage examples and exit",
    ),
    help_flag: Optional[bool] = Option(
        None,
        "--help",
        "-h",
        callback=_help_callback,
        is_eager=True,
        help="Show this message and exit",
    ),
) -> None:
    """
    Check Python docstring formatting and completeness.

    This tool analyzes Python files and validates that functions, methods, and classes
    have properly formatted docstrings according to the configured sections.
    """
    # If no subcommand is provided, show help
    if ctx.invoked_subcommand is None:
        echo(ctx.get_help())
        raise Exit()


@app.command(
    rich_help_panel="Commands",
    add_help_option=False,  # Disable automatic help so we can add our own with -h
)
def check(
    path: str = Argument(..., help="Path to Python file or directory to check"),
    config: Optional[str] = Option(None, "--config", "-c", help="Path to configuration file (TOML format)"),
    recursive: str = Option(
        "true",
        "--recursive",
        "-r",
        help="Check directories recursively (default: true). Accepts: true/false, t/f, yes/no, y/n, 1/0, on/off",
    ),
    exclude: Optional[list[str]] = Option(
        None,
        "--exclude",
        "-x",
        help="Glob patterns to exclude (can be used multiple times)",
    ),
    quiet: bool = Option(False, "--quiet", "-q", help="Only show errors, no success messages"),
    verbose: bool = Option(False, "--verbose", "-n", help="Show detailed output"),
    examples: Optional[bool] = Option(
        None,
        "--examples",
        "-e",
        callback=_show_check_examples_callback,
        is_eager=True,
        help="Show usage examples and exit",
    ),
    help_flag: Optional[bool] = Option(
        None,
        "--help",
        "-h",
        callback=_help_callback,
        is_eager=True,
        help="Show this message and exit",
    ),
) -> None:
    """
    Check docstrings in Python files.
    """
    # Parse the recursive string value into a boolean
    try:
        recursive_bool: bool = _parse_recursive_flag(recursive)
    except ValueError as e:
        raise BadParameter(
            message=(
                f"Invalid value for --recursive: '{recursive}'.{NEW_LINE}"
                "Use one of: true/false, t/f, yes/no, y/n, 1/0, or on/off."
            )
        ) from e
    _check_docstrings(path, config, recursive_bool, exclude, quiet, verbose)


@app.command(
    rich_help_panel="Commands",
    add_help_option=False,  # Disable automatic help so we can add our own with -h
)
def config_example(
    help_flag: Optional[bool] = Option(
        None,
        "--help",
        "-h",
        callback=_help_callback,
        is_eager=True,
        help="Show this message and exit",
    ),
) -> None:
    """
    Show example configuration file.
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
        """.strip()
    )

    print(example_config)


def entry_point() -> None:
    """Entry point for the CLI scripts defined in pyproject.toml."""
    app()


if __name__ == "__main__":
    app()
