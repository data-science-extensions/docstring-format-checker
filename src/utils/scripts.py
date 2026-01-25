# ============================================================================ #
#                                                                              #
#     Title: Scripts Utility                                                   #
#     Purpose: Collection of utility functions for scripting tasks such as     #
#         linting, checking, git operations, and documentation management.     #
#     Usage:                                                                   #
#         uv run ./src/utils/scripts.py <command> [args...]                    #
#     Examples:                                                                #
#         uv run ./src/utils/scripts.py lint                                   #
#         uv run ./src/utils/scripts.py check                                  #
#         uv run ./src/utils/scripts.py lint-check                             #
#     Notes: This script is designed to be run from the command line with      #
#         various commands to perform different tasks.                         #
#                                                                              #
# ============================================================================ #


## --------------------------------------------------------------------------- #
##  Setup                                                                   ####
## --------------------------------------------------------------------------- #


# ## Python StdLib Imports ----
import subprocess
import sys
from functools import lru_cache
from pathlib import Path
from textwrap import dedent
from typing import Union


## --------------------------------------------------------------------------- #
##  Constants                                                               ####
## --------------------------------------------------------------------------- #


PACKAGE_NAME: str = "docstring-format-checker"
DIRECTORY_NAME: str = PACKAGE_NAME.replace("-", "_")


## --------------------------------------------------------------------------- #
##  Generic                                                                 ####
## --------------------------------------------------------------------------- #


def expand_space(lst: Union[list[str], tuple[str, ...]]) -> list[str]:
    return [item for element in lst for item in element.split()]


def run_command(*command, expand: bool = True) -> None:
    _command: list[str] = expand_space(command) if expand else list(command)
    print("\n", " ".join(_command), sep="", flush=True)
    subprocess.run(_command, check=True, encoding="utf-8")


run = run_command


def uv_sync() -> None:
    run("uv sync --all-groups --native-tls --link-mode=copy")


def lint_check() -> None:
    lint()
    check()


@lru_cache
def get_all_files(*suffixes) -> list[str]:
    """
    !!! note "Summary"
        Get all files with the specified suffixes, excluding .venv and hidden directories.
        Uses `find` for performance or defaulting back to `Path.glob`.
    """
    try:
        find_cmd: list[str] = [
            "find",
            ".",
            "-name",
            ".venv",
            "-prune",
            "-o",
            "-name",
            ".*",
            "-not",
            "-name",
            ".",
            "-prune",
            "-o",
            "-type",
            "f",
        ]
        if suffixes:
            find_cmd.append("(")
            for i, s in enumerate(suffixes):
                if i > 0:
                    find_cmd.append("-o")
                find_cmd.append("-name")
                find_cmd.append(f"*{s}")
            find_cmd.append(")")
        find_cmd.append("-print")
        output: str = subprocess.check_output(find_cmd, text=True, stderr=subprocess.DEVNULL)
        return sorted([f.removeprefix("./") for f in output.splitlines() if f])
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback to Path.glob
        return sorted(
            [
                str(p)
                for p in Path("./").glob("**/*")
                if ".venv" not in p.parts and not p.parts[0].startswith(".") and p.is_file() and p.suffix in {*suffixes}
            ]
        )


## --------------------------------------------------------------------------- #
##  Linting                                                                 ####
## --------------------------------------------------------------------------- #


def run_black() -> None:
    run("black --config=pyproject.toml ./")


def run_blacken_docs() -> None:
    """
    !!! note "Summary"
        Run blacken-docs on all markdown, Python, and notebook files.

    !!! note "Behaviour"
        Automatically re-run if files are rewritten to ensure formatting is stable.
        Only halt if there's a parsing error (cannot parse error message).
    """

    max_attempts: int = 3
    attempt: int = 0

    while attempt < max_attempts:

        attempt += 1
        files: list[str] = get_all_files(".md", ".py", ".ipynb")
        _command: list[str] = ["blacken-docs", *files]

        print(f"\n{'Attempt ' + str(attempt) + ': ' if attempt > 1 else ''}{' '.join(_command)}", flush=True)

        result = subprocess.run(_command, check=False, encoding="utf-8", capture_output=True)

        # Print stdout and stderr
        if result.stdout:
            print(result.stdout, end="", flush=True)
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr, flush=True)

        # Check for parsing errors (exit code 2 or "cannot parse" message)
        # These should halt execution immediately
        output_combined: str = ((result.stdout or "") + (result.stderr or "")).lower()
        if result.returncode == 2 or "cannot parse" in output_combined or "parse error" in output_combined:
            print(f"\n❌ blacken-docs encountered a parsing error. Halting.", file=sys.stderr, flush=True)
            raise subprocess.CalledProcessError(result.returncode, _command, result.stdout, result.stderr)

        # If exit code is 0, formatting is stable - success!
        if result.returncode == 0:
            if attempt > 1:
                print(f"✅ blacken-docs formatting stabilised after {attempt} attempts.", flush=True)
            return

        # Exit code 1 typically means files were rewritten
        # Re-run to ensure formatting is stable
        if attempt < max_attempts:
            print(
                f"⚠️  Files were rewritten. Re-running blacken-docs (attempt {attempt + 1}/{max_attempts})...",
                flush=True,
            )
        else:
            print(
                f"⚠️  blacken-docs still making changes after {max_attempts} attempts. This may indicate an issue.",
                file=sys.stderr,
                flush=True,
            )
            raise subprocess.CalledProcessError(result.returncode, _command, result.stdout, result.stderr)


def run_isort() -> None:
    run("isort --settings-file=pyproject.toml ./")


def run_pycln() -> None:
    run("pycln --config=pyproject.toml src/")


def run_pyupgrade() -> None:
    run("pyupgrade --py3-plus", *get_all_files(".py"))


def lint() -> None:
    run_black()
    run_blacken_docs()
    run_isort()
    run_pycln()


## --------------------------------------------------------------------------- #
##  Checking                                                                ####
## --------------------------------------------------------------------------- #


def check_black() -> None:
    run("black --check --config=pyproject.toml ./")


def check_blacken_docs() -> None:
    run("blacken-docs --check", *get_all_files(".md", ".py", ".ipynb"))


def check_ty() -> None:
    run(f"ty check ./src/{DIRECTORY_NAME}")


def check_isort() -> None:
    run("isort --check --settings-file=pyproject.toml ./")


def check_codespell() -> None:
    run("codespell --toml=pyproject.toml src/ *.py")


def check_pylint() -> None:
    run(f"pylint --rcfile=pyproject.toml src/{DIRECTORY_NAME}")


def check_pyright() -> None:
    run(f"pyright ./src/{DIRECTORY_NAME}")


def check_pycln() -> None:
    run("pycln --check --config=pyproject.toml src/")


def check_build() -> None:
    run("uv build --out-dir=dist")
    run("rm -r dist")


def check_mkdocs() -> None:
    run("mkdocs build --site-dir=temp")
    run("rm -r temp")


def check_pytest() -> None:
    run("pytest --config-file=pyproject.toml")


def check_docstrings() -> None:
    run(f"dfc --output=table ./src/{DIRECTORY_NAME}")


def check_complexity() -> None:
    notes: str = dedent(
        """
        Notes from: https://rohaquinlop.github.io/complexipy/#running-the-analysis
        - Complexity <= 5: Simple, easy to understand
        - Complexity 6-15: Moderate, acceptable for most cases
        - Complexity >= 15: Complex, consider refactoring into simpler functions
        """
    )
    print(notes)
    run(f"complexipy ./src/{DIRECTORY_NAME}")


def check_doctest() -> None:
    run(
        "pytest --verbose  --verbose --doctest-modules --doctest-continue-on-failure",
        *[file for file in get_all_files(".py") if DIRECTORY_NAME in file],
    )


def check_doctest_module(module_name: str) -> None:
    run(
        "pytest --verbose  --verbose --doctest-modules --doctest-continue-on-failure",
        *[file for file in get_all_files(".py") if DIRECTORY_NAME in file and module_name in file],
    )


def check_doctest_cli() -> None:
    if len(sys.argv) < 3:
        print("Requires argument: <module_name>")
        sys.exit(1)
    check_doctest_module(sys.argv[2])


def check() -> None:
    check_black()
    check_blacken_docs()
    check_ty()
    check_isort()
    check_codespell()
    check_pycln()
    check_pylint()
    check_pyright()
    check_complexity()
    check_docstrings()
    check_pytest()
    check_build()
    check_mkdocs()


## --------------------------------------------------------------------------- #
##  Git                                                                     ####
## --------------------------------------------------------------------------- #


def add_git_credentials() -> None:
    run("git config --global user.name github-actions[bot]")
    run("git config --global user.email github-actions[bot]@users.noreply.github.com")


def git_refresh_current_branch() -> None:
    run("git remote update")
    run("git fetch --verbose")
    run("git fetch --verbose --tags")
    run("git pull --verbose")
    run("git status --verbose")
    run("git branch --list --verbose")
    run("git tag --list --sort=-creatordate")


def git_checkout_branch(branch_name: str) -> None:
    run(f"git checkout -B {branch_name} --track origin/{branch_name}")


def git_switch_to_branch() -> None:
    if len(sys.argv) < 2:
        print("Requires argument: <branch_name>")
        sys.exit(1)
    git_checkout_branch(sys.argv[2])


def git_switch_to_main_branch() -> None:
    git_checkout_branch("main")


def git_switch_to_docs_branch() -> None:
    git_checkout_branch("docs-site")


def git_add_coverage_report() -> None:
    run("mkdir -p ./docs/code/coverage/")
    run("cp -r ./cov-report/html/. ./docs/code/coverage/")
    run("git add ./docs/code/coverage/ --force")
    run("git", "commit", "--no-verify", '--message="Update coverage report [skip ci]"', expand=False)
    run("git push")


def git_update_version(version: str) -> None:
    run(f'echo VERSION="{version}"')
    run("git add .")
    run("git", "commit", "--allow-empty", f'--message="Bump to version `{version}` [skip ci]"', expand=False)
    run("git push --force --no-verify")
    run("git status")


def git_update_version_cli() -> None:
    if len(sys.argv) < 2:
        print("Requires argument: <version>")
        sys.exit(1)
    git_update_version(sys.argv[2])


def git_fix_tag_reference(version: str) -> None:
    run(f"git tag --force {version}")
    run(f"git push --force origin {version}")


def git_fix_tag_reference_cli() -> None:
    if len(sys.argv) < 2:
        print("Requires argument: <version>")
        sys.exit(1)
    git_fix_tag_reference(sys.argv[2])


## --------------------------------------------------------------------------- #
##  Docs                                                                    ####
## --------------------------------------------------------------------------- #


def docs_serve_static() -> None:
    run("mkdocs serve")


def docs_serve_versioned() -> None:
    run("mike serve --branch=docs-site")


def docs_build_static() -> None:
    run("mkdocs build --clean")


def docs_build_versioned(version: str) -> None:
    run("git config --global --list")
    run("git config --local --list")
    run("git remote --verbose")
    run(f"mike --debug deploy --update-aliases --branch=docs-site --push {version} latest")


def docs_build_versioned_cli() -> None:
    if len(sys.argv) < 2:
        print("Requires argument: <version>")
        sys.exit(1)
    docs_build_versioned(sys.argv[2])


def update_git_docs(version: str) -> None:
    run("git add .")
    run("git", "commit", f'--message="Build docs `{version}` [skip ci]"', expand=False)
    run("git push --force --no-verify --push-option ci.skip")


def update_git_docs_cli() -> None:
    if len(sys.argv) < 2:
        print("Requires argument: <version>")
        sys.exit(1)
    update_git_docs(sys.argv[2])


def docs_check_versions() -> None:
    run("mike --debug list --branch=docs-site")


def docs_delete_version(version: str) -> None:
    run(f"mike --debug delete --branch=docs-site {version}")


def docs_delete_version_cli() -> None:
    if len(sys.argv) < 2:
        print("Requires argument: <version>")
        sys.exit(1)
    docs_delete_version(sys.argv[2])


def docs_set_default() -> None:
    run("mike --debug set-default --branch=docs-site --push latest")


def build_static_docs(version: str) -> None:
    docs_build_static()
    update_git_docs(version)


def build_static_docs_cli() -> None:
    if len(sys.argv) < 2:
        print("Requires argument: <version>")
        sys.exit(1)
    build_static_docs(sys.argv[2])


def build_versioned_docs(version: str) -> None:
    docs_build_versioned(version)
    docs_set_default()


def build_versioned_docs_cli() -> None:
    if len(sys.argv) < 2:
        print("Requires argument: <version>")
        sys.exit(1)
    build_versioned_docs(sys.argv[2])


## --------------------------------------------------------------------------- #
##  Executor                                                                ####
## --------------------------------------------------------------------------- #


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts.py <command> [args...]")
        sys.exit(1)
    command: str = sys.argv[1].replace("-", "_")
    if command in globals():
        globals()[command]()
    else:
        print(f"Unknown command: {sys.argv[1]}")
        sys.exit(1)
