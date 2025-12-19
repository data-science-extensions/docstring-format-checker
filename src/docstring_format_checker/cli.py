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
import os
from functools import partial
from pathlib import Path
from textwrap import dedent
from typing import Optional

# ## Python Third Party Imports ----
import pyfiglet
from rich.console import Console
from rich.markup import escape
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
    "check_docstrings",
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
    """
    !!! note "Summary"
        Apply Rich colour markup to text.

    Params:
        text (str):
            The text to colour.
        colour (str):
            The colour to apply, e.g., 'red', 'green', 'blue'.

    Returns:
        (str):
            The text wrapped in Rich colour markup.
    """
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
    raise Exit()


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
        Execute the below commands in any terminal after installing the package.

        {_blue("dfc myfile.py")}                   {_green("# Check a single Python file (list output)")}
        {_blue("dfc myfile.py other_file.py")}     {_green("# Check multiple Python files")}
        {_blue("dfc src/")}                        {_green("# Check all Python files in src/ directory")}
        {_blue("dfc -x src/app/__init__.py src/")} {_green("# Check all Python files in src/ directory, excluding one init file")}
        {_blue("dfc --output=table myfile.py")}    {_green("# Check with table output format")}
        {_blue("dfc -o list myfile.py")}           {_green("# Check with list output format (default)")}
        {_blue("dfc --check myfile.py")}           {_green("# Check and exit with error if issues found")}
        {_blue("dfc --quiet myfile.py")}           {_green("# Check quietly, only show pass/fail")}
        {_blue("dfc --quiet --check myfile.py")}   {_green("# Check quietly and exit with error if issues found")}
        {_blue("dfc . --exclude '*/tests/*'")}     {_green("# Check current directory, excluding tests")}
        {_blue("dfc . -c custom.toml")}            {_green("# Use custom configuration file")}
        {_blue("dfc --example=config")}            {_green("# Show example configuration")}
        {_blue("dfc -e usage")}                    {_green("# Show usage examples (this help)")}
        """
    ).strip()

    panel = Panel(
        examples_content,
        title="Usage Examples",
        title_align="left",
        border_style="dim",
        padding=(0, 1),
    )

    console.print(panel)


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
        r"""
        Place the below config in your `pyproject.toml` file.

        [blue]\[tool.dfc][/blue]
        [green]# or \[tool.docstring-format-checker][/green]
        [blue]allow_undefined_sections = false[/blue]
        [blue]require_docstrings = true[/blue]
        [blue]check_private = true[/blue]
        [blue]validate_param_types = true[/blue]
        [blue]optional_style = "validate"[/blue]  [green]# "silent", "validate", or "strict"[/green]
        [blue]sections = [[/blue]
            [blue]{ order = 1, name = "summary",  type = "free_text",          required = true, admonition = "note", prefix = "!!!" },[/blue]
            [blue]{ order = 2, name = "details",  type = "free_text",          required = false, admonition = "abstract", prefix = "???+" },[/blue]
            [blue]{ order = 3, name = "params",   type = "list_name_and_type", required = false },[/blue]
            [blue]{ order = 4, name = "raises",   type = "list_type",          required = false },[/blue]
            [blue]{ order = 5, name = "returns",  type = "list_name_and_type", required = false },[/blue]
            [blue]{ order = 6, name = "yields",   type = "list_type",          required = false },[/blue]
            [blue]{ order = 7, name = "examples", type = "free_text",          required = false, admonition = "example", prefix = "???+" },[/blue]
            [blue]{ order = 8, name = "notes",    type = "free_text",          required = false, admonition = "note", prefix = "???" },[/blue]
        [blue]][/blue]
        """
    ).strip()

    panel = Panel(
        example_config,
        title="Configuration Example",
        title_align="left",
        border_style="dim",
        padding=(0, 1),
    )

    # Print without Rich markup processing to avoid bracket interpretation
    console.print(panel)


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

    # Early exit if help flag is set
    if not value or ctx.resilient_parsing:
        return

    # Determine terminal width for ASCII art
    try:
        terminal_width: int = os.get_terminal_size().columns
    except OSError:
        terminal_width = 80

    # Determine title based on terminal width
    title: str = "dfc" if terminal_width < 130 else "docstring-format-checker"

    # Print ASCII art title
    console.print(
        pyfiglet.figlet_format(title, font="standard", justify="left", width=140),
        style="magenta",
        markup=False,
    )

    # Show help message
    echo(ctx.get_help())

    # Show usage and config examples
    _show_usage_examples_callback()
    _show_config_example_callback()

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

    # Single error message
    else:
        return f"- {error_message.strip()}."


def _display_results(
    results: dict[str, list[DocstringError]],
    quiet: bool,
    output: str,
    check: bool,
) -> int:
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
            console.print(_green("✅ All docstrings are valid!"))
        return 0

    # Count errors and generate summary statistics
    error_stats = _count_errors_and_files(results)

    if quiet:
        _display_quiet_summary(error_stats)
        return 1

    # Display detailed results based on output format
    if output == "table":
        _display_table_output(results)
    else:
        _display_list_output(results)

    # Display final summary
    _display_final_summary(error_stats)
    return 1


def _count_errors_and_files(results: dict[str, list[DocstringError]]) -> dict[str, int]:
    """
    !!! note "Summary"
        Count total errors, functions, and files from results.

    Params:
        results (dict[str, list[DocstringError]]):
            Dictionary mapping file paths to lists of errors.

    Returns:
        (dict[str, int]):
            Dictionary containing total_errors, total_functions, and total_files.
    """
    total_individual_errors: int = 0
    total_functions: int = 0

    for errors in results.values():
        total_functions += len(errors)
        for error in errors:
            if "; " in error.message:
                individual_errors: list[str] = [msg.strip() for msg in error.message.split("; ") if msg.strip()]
                total_individual_errors += len(individual_errors)
            else:
                total_individual_errors += 1

    return {"total_errors": total_individual_errors, "total_functions": total_functions, "total_files": len(results)}


def _display_quiet_summary(error_stats: dict[str, int]) -> None:
    """
    !!! note "Summary"
        Display summary in quiet mode.

    Params:
        error_stats (dict[str, int]):
            Dictionary containing total_errors, total_functions, and total_files.
    """
    functions_text = (
        "1 function" if error_stats["total_functions"] == 1 else f"{error_stats['total_functions']} functions"
    )
    files_text: str = "1 file" if error_stats["total_files"] == 1 else f"{error_stats['total_files']} files"

    console.print(_red(f"{NEW_LINE}Found {error_stats['total_errors']} error(s) in {functions_text} over {files_text}"))


def _display_table_output(results: dict[str, list[DocstringError]]) -> None:
    """
    !!! note "Summary"
        Display results in table format.

    Params:
        results (dict[str, list[DocstringError]]):
            Dictionary mapping file paths to lists of errors.
    """
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("File", style="cyan", no_wrap=False)
    table.add_column("Line", justify="right", style="white")
    table.add_column("Item", style="yellow")
    table.add_column("Type", style="blue")
    table.add_column("Error", style="red")

    for file_path, errors in results.items():
        for i, error in enumerate(errors):
            file_display = file_path if i == 0 else ""
            formatted_error_message = _format_error_messages(error.message)

            table.add_row(
                file_display,
                str(error.line_number) if error.line_number > 0 else "",
                error.item_name,
                error.item_type,
                f"[red]{formatted_error_message}[/red]",
            )
    console.print(table)


def _create_error_header(error: DocstringError) -> str:
    """
    !!! note "Summary"
        Create formatted header for a single error.

    Params:
        error (DocstringError):
            The error to create a header for.

    Returns:
        (str):
            Formatted header string with line number, item type, and name.
    """
    if error.line_number > 0:
        return f"  [red]Line {error.line_number}[/red] - {error.item_type} '{error.item_name}':"
    else:
        return f"  {_red('Error')} - {error.item_type} '{error.item_name}':"


def _split_error_messages(message: str) -> list[str]:
    """
    !!! note "Summary"
        Split compound error message into individual messages.

    Params:
        message (str):
            The error message to split.

    Returns:
        (list[str]):
            List of individual error messages.
    """
    if "; " in message:
        return [msg.strip() for msg in message.split("; ") if msg.strip()]
    else:
        return [message.strip()]


def _format_error_output(error: DocstringError) -> list[str]:
    """
    !!! note "Summary"
        Format single error for display output.

    Params:
        error (DocstringError):
            The error to format.

    Returns:
        (list[str]):
            List of formatted lines to print.
    """
    lines: list[str] = [_create_error_header(error)]
    individual_errors: list[str] = _split_error_messages(error.message)

    for individual_error in individual_errors:
        # Escape square brackets for Rich markup using Rich's escape function
        individual_error: str = escape(individual_error)

        # Check if this error has multi-line content (e.g., parameter type mismatches)
        if "\n" in individual_error:
            # Split by newlines and add 4 spaces of extra indentation to each line
            error_lines: list[str] = individual_error.split("\n")
            lines.append(f"    - {error_lines[0]}")  # First line gets the bullet
            for sub_line in error_lines[1:]:
                if sub_line.strip():  # Only add non-empty lines
                    lines.append(f"    {sub_line}")  # Continuation lines get 4 spaces
        else:
            lines.append(f"    - {individual_error}")

    return lines


def _display_list_output(results: dict[str, list[DocstringError]]) -> None:
    """
    !!! note "Summary"
        Display results in list format.

    Params:
        results (dict[str, list[DocstringError]]):
            Dictionary mapping file paths to lists of errors.
    """
    for file_path, errors in results.items():
        console.print(f"{NEW_LINE}{_cyan(file_path)}")
        for error in errors:
            output_lines: list[str] = _format_error_output(error)
            for line in output_lines:
                console.print(line)


def _display_final_summary(error_stats: dict[str, int]) -> None:
    """
    !!! note "Summary"
        Display the final summary line.

    Params:
        error_stats (dict[str, int]):
            Dictionary containing total_errors, total_functions, and total_files.
    """
    functions_text: str = (
        "1 function" if error_stats["total_functions"] == 1 else f"{error_stats['total_functions']} functions"
    )
    files_text: str = "1 file" if error_stats["total_files"] == 1 else f"{error_stats['total_files']} files"

    console.print(_red(f"{NEW_LINE}Found {error_stats['total_errors']} error(s) in {functions_text} over {files_text}"))


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Main Logic                                                            ####
#                                                                              #
# ---------------------------------------------------------------------------- #


# This will be the default behavior when no command is specified
def check_docstrings(
    paths: list[str],
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
        paths (list[str]):
            The path(s) to the file(s) or directory(ies) to check.
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
    # Validate and process input paths
    target_paths: list[Path] = _validate_and_process_paths(paths)

    # Load and validate configuration
    config_obj: Config = _load_and_validate_config(config, target_paths)

    # Initialize checker and process all paths
    checker = DocstringChecker(config_obj)
    all_results: dict[str, list[DocstringError]] = _process_all_paths(checker, target_paths, exclude)

    # Display results and handle exit
    exit_code: int = _display_results(all_results, quiet, output, check)
    if exit_code != 0:
        raise Exit(exit_code)


def _validate_and_process_paths(paths: list[str]) -> list[Path]:
    """
    !!! note "Summary"
        Validate input paths and return valid paths.

    Params:
        paths (list[str]):
            List of path strings to validate.

    Raises:
        (Exit):
            If any paths do not exist.

    Returns:
        (list[Path]):
            List of valid Path objects.
    """
    path_objs: list[Path] = [Path(path) for path in paths]
    target_paths: list[Path] = [p for p in path_objs if p.exists()]
    invalid_paths: list[Path] = [p for p in path_objs if not p.exists()]

    if invalid_paths:
        console.print(
            _red("[bold]Error: Paths do not exist:[/bold]"),
            NEW_LINE,
            NEW_LINE.join([f"- '{invalid_path}'" for invalid_path in invalid_paths]),
        )
        raise Exit(1)

    return target_paths


def _load_and_validate_config(config: Optional[str], target_paths: list[Path]) -> Config:
    """
    !!! note "Summary"
        Load and validate configuration from file or auto-discovery.

    Params:
        config (Optional[str]):
            Optional path to configuration file.
        target_paths (list[Path]):
            List of target paths for auto-discovery.

    Raises:
        (Exit):
            If configuration loading fails.

    Returns:
        (Config):
            Loaded configuration object.
    """
    try:
        if config:
            return _load_explicit_config(config)
        else:
            return _load_auto_discovered_config(target_paths)
    except Exception as e:
        console.print(_red(f"Error loading configuration: {e}"))
        raise Exit(1) from e


def _load_explicit_config(config: str) -> Config:
    """
    !!! note "Summary"
        Load configuration from explicitly specified path.

    Params:
        config (str):
            Path to configuration file.

    Raises:
        (Exit):
            If configuration file does not exist.

    Returns:
        (Config):
            Loaded configuration object.
    """
    config_path = Path(config)
    if not config_path.exists():
        console.print(_red(f"Error: Configuration file does not exist: {config}"))
        raise Exit(1)
    return load_config(config_path)


def _load_auto_discovered_config(target_paths: list[Path]) -> Config:
    """
    !!! note "Summary"
        Load configuration from auto-discovery or defaults.

    Params:
        target_paths (list[Path]):
            List of target paths to search for configuration.

    Returns:
        (Config):
            Loaded configuration object from found config or defaults.
    """
    first_path: Path = target_paths[0]
    search_path: Path = first_path if first_path.is_dir() else first_path.parent
    found_config: Optional[Path] = find_config_file(search_path)

    if found_config:
        return load_config(found_config)
    else:
        return load_config()


def _process_all_paths(
    checker: DocstringChecker, target_paths: list[Path], exclude: Optional[list[str]]
) -> dict[str, list[DocstringError]]:
    """
    !!! note "Summary"
        Process all target paths and collect docstring errors.

    Params:
        checker (DocstringChecker):
            The checker instance to use.
        target_paths (list[Path]):
            List of paths to check (files or directories).
        exclude (Optional[list[str]]):
            Optional list of exclusion patterns.

    Raises:
        (Exit):
            If an error occurs during checking.

    Returns:
        (dict[str, list[DocstringError]]):
            Dictionary mapping file paths to lists of errors.
    """
    all_results: dict[str, list[DocstringError]] = {}

    try:
        for target_path in target_paths:
            if target_path.is_file():
                errors: list[DocstringError] = checker.check_file(target_path)
                if errors:
                    all_results[str(target_path)] = errors
            else:
                directory_results: dict[str, list[DocstringError]] = checker.check_directory(
                    target_path, exclude_patterns=exclude
                )
                all_results.update(directory_results)
    except Exception as e:
        console.print(_red(f"Error during checking: {e}"))
        raise Exit(1) from e

    return all_results


# ---------------------------------------------------------------------------- #
#                                                                              #
#     App Operators                                                         ####
#                                                                              #
# ---------------------------------------------------------------------------- #


# Simple callback that only handles global options and delegates to subcommands
@app.callback(invoke_without_command=True)
def main(
    ctx: Context,
    paths: Optional[list[str]] = Argument(None, help="Path(s) to Python file(s) or directory(s) for DFC to check"),
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
        paths (Optional[list[str]]):
            Path(s) to Python file(s) or directory(ies) to check.
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

    # If no paths are provided, show help
    if not paths:
        echo(ctx.get_help())
        raise Exit(0)

    # Validate output format
    if output not in ["table", "list"]:
        console.print(_red(f"Error: Invalid output format '{output}'. Use 'table' or 'list'."))
        raise Exit(1)

    check_docstrings(
        paths=paths,
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
