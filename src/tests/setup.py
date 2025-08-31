# ---------------------------------------------------------------------------- #
#                                                                              #
#     Setup                                                                 ####
#                                                                              #
# ---------------------------------------------------------------------------- #


## --------------------------------------------------------------------------- #
##  Imports                                                                 ####
## --------------------------------------------------------------------------- #


# ## Python StdLib Imports ----
import re
from typing import Any, Callable, Union


## --------------------------------------------------------------------------- #
##  Exports                                                                 ####
## --------------------------------------------------------------------------- #


__all__: list[str] = [
    "name_func_flat_list",
    "name_func_nested_list",
    "name_func_predefined_name",
]


## --------------------------------------------------------------------------- #
##  Helper functions                                                        ####
## --------------------------------------------------------------------------- #


def name_func_flat_list(
    func: Callable,
    idx: int,
    params: Union[tuple[Any, ...], list[Any]],
) -> str:
    return f"{func.__name__}_{int(idx)+1:02}_{'_'.join([str(param) for param in params[0]])}"


def name_func_nested_list(
    func: Callable,
    idx: int,
    params: Union[
        list[Union[tuple[Any, ...], list[Any]]],
        tuple[Union[tuple[Any, ...], list[Any]], ...],
    ],
) -> str:
    return f"{func.__name__}_{int(idx)+1:02}_{params[0][0]}_{params[0][1]}"


def name_func_predefined_name(
    func: Callable,
    idx: int,
    params: Union[tuple[Any, ...], list[Any]],
) -> str:
    return f"{func.__name__}_{int(idx)+1:02}_{params[0][0]}"


def strip_ansi_codes(text: str) -> str:
    r"""
    !!! note "Summary"
        Remove ANSI escape sequences from text.

    ???+ abstract "Details"
        This is needed for robust testing of CLI output that may contain formatting codes in different environments (e.g., CI vs local).
        This function solves a testing consistency problem where CLI applications (like those using Typer/Rich) output different text formatting in different environments:
        - **Locally**: Plain text output
        - **CI environments**: Text with ANSI escape codes for colors/formatting

    ???+ info "Notes"

        How it Works:
        - **Input**: Takes a string that may contain ANSI escape sequences
        - **Regex Pattern**: r"\x1b\[[0-?]*[ -/]*[@-~]"
        - **Processing**: Uses re.sub() to replace all ANSI sequences with empty strings
        - **Output**: Returns clean text without any formatting codes

        Breaking Down the Regex Pattern:
            The regex `r"\x1b\[[0-?]*[ -/]*[@-~]"` is specifically designed to match ANSI escape sequences:
            - `\x1b`: Literal ESC character (ASCII 27, hex 1B)
            - `\[`: Literal opening bracket `[`
            - `[0-?]*`: Zero or more characters in range `0-9`, `:`, `;`, `<`, `=`, `>`, `?`
            - `[ -/]*`: Zero or more characters in range ` ` (space) through `/`
            - `[@-~]`: Final character in range `@` through `~` (terminates the sequence)

        Example Transformations:
        - **Before** (with ANSI codes):
            ```txt
            \x1b[1m--recursive\x1b[0m
            ```
        - **After** (clean text):
            ```txt
            --recursive
            ```

        Real-World Context:
        - In the failing CI tests, Typer was outputting error messages like:
            ```txt
            Invalid value for \x1b[1m--recursive\x1b[0m: 'invalid'
            ```
        - The test was looking for the literal string `"--recursive"`, but the ANSI codes made it not match. This function strips those codes so the test can find the expected text regardless of environment.

        Why This Is Necessary:
        - **Rich/Typer libraries** add formatting codes even when colors are "disabled"
        - **CI environments** often behave differently than local development
        - **Tests need to be robust** across different terminal capabilities
        - **String matching** becomes unreliable with formatting codes present

        Final Comment:
        - This function enables **environment-agnostic testing** by normalizing the CLI output to plain text that can be consistently checked across local development and CI environments.
    """
    ansi_escape: re.Pattern[str] = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
    return ansi_escape.sub("", text)
