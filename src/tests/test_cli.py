# ============================================================================ #
#                                                                              #
#     Title: CLI Tests                                                         #
#     Purpose: Test the command-line interface functionality                   #
#     Notes: Tests for docstring-format-checker CLI                           #
#     Author: chrimaho                                                         #
#     Created: 2025-08-03                                                      #
#                                                                              #
# ============================================================================ #


"""
!!! note "Summary"
    Tests for the command-line interface.
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
import tempfile
from pathlib import Path
from textwrap import dedent
from unittest import TestCase

# ## Python Third Party Imports ----
import typer
from click.testing import Result
from parameterized import parameterized
from pytest import raises
from typer.testing import CliRunner

# ## Local First Party Imports ----
from docstring_format_checker import __version__
from docstring_format_checker.cli import app, version_callback
from tests.setup import name_func_flat_list


## --------------------------------------------------------------------------- #
##  Test Class                                                              ####
## --------------------------------------------------------------------------- #


class TestCLI(TestCase):
    """
    Test CLI functionality.
    """

    def setUp(self) -> None:
        """
        Set up test fixtures.
        """

        self.runner = CliRunner()

    def test_01_help_message(self) -> None:
        """
        Test help message is displayed.
        """

        result: Result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "A CLI tool to check and validate Python docstring formatting" in result.output

    def test_02_version_callback(self) -> None:
        """
        Test version callback functionality.
        """

        with raises(typer.Exit):
            version_callback(True)

    def test_03_version_option(self) -> None:
        """
        Test --version option.
        """

        result: Result = self.runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert f"docstring-format-checker version {__version__}" in result.output

    def test_04_no_arguments_shows_help(self) -> None:
        """
        Test that no arguments shows help.
        """

        result: Result = self.runner.invoke(app, [])
        assert result.exit_code == 0  # Now shows help successfully
        assert "Usage:" in result.output
        assert "A CLI tool to check and validate Python docstring formatting and completeness" in result.output

    def test_05_config_example_command(self) -> None:
        """
        Test config-example command.
        """

        result: Result = self.runner.invoke(app, ["config-example"])
        print(result)
        print(result.output)
        if result.exit_code != 0:
            print(f"{result.exit_code=}")
            print(f"{result.output=}")
        assert result.exit_code == 0
        assert "[tool.dfc]" in result.output
        assert "[[tool.dfc.sections]]" in result.output

    def test_06_nonexistent_file(self) -> None:
        """
        Test error handling for nonexistent file.
        """

        result: Result = self.runner.invoke(app, ["check", "nonexistent.py"])
        assert result.exit_code == 1
        assert "Error: Path does not exist" in result.output

    def test_07_check_valid_python_file(self) -> None:
        """
        Test checking a valid Python file.
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:

            f.write(
                dedent(
                    '''
                    def good_function():
                        """
                        !!! note "Summary"
                            This function has a good docstring.

                        ???+ info "Details"
                            More detailed information here.

                        Args:
                            None

                        Returns:
                            None
                        """
                        pass
                    '''
                )
            )

            f.flush()

            try:
                result: Result = self.runner.invoke(app, ["check", f.name])
                # Should succeed with default config
                assert result.exit_code == 0 or "All docstrings are valid" in result.output
            finally:
                Path(f.name).unlink()

    def test_08_check_invalid_python_file(self) -> None:
        """
        Test checking a Python file with missing docstrings.
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:

            f.write(
                dedent(
                    """
                    def bad_function():
                        pass

                    class BadClass:
                        def bad_method(self):
                            return None
                    """
                )
            )

            f.flush()

            try:
                result: Result = self.runner.invoke(app, ["check", f.name])

                if result.exit_code != 1:
                    print(f"{result.exit_code=}")
                    print(f"{result.output=}")

                # Should fail due to missing docstrings
                assert result.exit_code == 1
                assert "error" in result.output.lower()
            finally:
                Path(f.name).unlink()

    def test_09_check_directory(self) -> None:
        """
        Test checking a directory.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            temp_path = Path(temp_dir)

            # Create a Python file with missing docstrings
            py_file: Path = temp_path / "test.py"
            py_file.write_text(
                dedent(
                    """
                    def function_without_docstring():
                        pass
                    """
                )
            )

            result: Result = self.runner.invoke(app, ["check", str(temp_path)])

            if result.exit_code != 1:
                print(f"{result.exit_code=}")
                print(f"{result.output=}")

            # Should find issues in the directory
            assert result.exit_code == 1

    def test_10_check_directory_non_recursive(self) -> None:
        """
        Test checking a directory non-recursively using --recursive=false.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            temp_path = Path(temp_dir)

            # Create subdirectory with Python file
            subdir: Path = temp_path / "subdir"
            subdir.mkdir()
            py_file: Path = subdir / "test.py"
            py_file.write_text("def func(): pass")

            result: Result = self.runner.invoke(app, ["check", "--recursive=false", str(temp_path)])

            # Should succeed because it doesn't check subdirectories
            assert result.exit_code == 0

    def test_11_exclude_patterns(self) -> None:
        """
        Test excluding files with patterns.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            temp_path = Path(temp_dir)

            # Create files
            test_file: Path = temp_path / "test_something.py"
            test_file.write_text("def func(): pass")

            regular_file: Path = temp_path / "regular.py"
            regular_file.write_text("def func(): pass")

            # Exclude test files
            result: Result = self.runner.invoke(app, ["check", "--exclude", "test_*.py", str(temp_path)])

            if result.exit_code != 1:
                print(f"{result.exit_code=}")
                print(f"{result.output=}")

            # Should only check regular.py and find issues
            assert result.exit_code == 1

    def test_12_quiet_option(self) -> None:
        """
        Test quiet option suppresses success messages.
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:

            f.write(
                dedent(
                    '''
                    def good_function():
                        """
                        !!! note "Summary"
                            This function has a good docstring.
                        """
                        pass
                    '''
                )
            )

            f.flush()

            try:
                result: Result = self.runner.invoke(app, ["check", "--quiet", f.name])
                # Should succeed without any output
                assert result.exit_code == 0
                assert result.output.strip() == ""
            finally:
                Path(f.name).unlink()

    def test_13_verbose_option(self) -> None:
        """
        Test verbose option shows detailed output.
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:

            f.write("def func(): pass")
            f.flush()

            try:
                result: Result = self.runner.invoke(app, ["check", "--verbose", f.name])
                # Should show detailed output
                assert "Checking file:" in result.output or "Using" in result.output
            finally:
                Path(f.name).unlink()

    def test_14_custom_config_file(self) -> None:
        """
        Test using a custom configuration file.
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as config_f:

            config_f.write(
                dedent(
                    """
                    [tool.dfc]
                    [[tool.dfc.sections]]
                    order = 1
                    name = "summary"
                    type = "free_text"
                    required = true
                    """
                )
            )

            config_f.flush()

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as py_f:

                py_f.write("def func(): pass")
                py_f.flush()

                try:
                    result: Result = self.runner.invoke(app, ["check", "--config", config_f.name, py_f.name])

                    if result.exit_code != 1:
                        print(f"{result.exit_code=}")
                        print(f"{result.output=}")

                    # Should use the custom config
                    assert result.exit_code == 1  # Missing docstrings
                finally:
                    Path(config_f.name).unlink()
                    Path(py_f.name).unlink()

    def test_15_nonexistent_config_file(self) -> None:
        """
        Test error handling for nonexistent config file.
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:

            f.write("def func(): pass")
            f.flush()

            try:
                result: Result = self.runner.invoke(app, ["check", "--config", "nonexistent.toml", f.name])
                assert result.exit_code == 1
                assert "Configuration file does not exist" in result.output
            finally:
                Path(f.name).unlink()

    @parameterized.expand(
        input=[
            "--recursive=true",
            "--recursive=t",
            "--recursive=yes",
            "--recursive=y",
            "--recursive=1",
            "--recursive=on",
            "--recursive true",
            "--recursive t",
            "--recursive yes",
            "--recursive y",
            "--recursive 1",
            "--recursive on",
            "--recursive=TRUE",
            "--recursive=True",
            "--recursive=YES",
            "--recursive=Yes",
            "-r true",
            "-r t",
            "-r yes",
            "-r y",
            "-r 1",
            "-r on",
            "-r T",
        ],
        name_func=name_func_flat_list,
    )
    def test_16_recursive_option_true_variants(self, true_variant: str) -> None:
        """
        Test that various 'true' values work for --recursive option.
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create subdirectory with Python file that has docstring issues
            subdir: Path = temp_path / "subdir"
            subdir.mkdir()
            py_file: Path = subdir / "test.py"
            py_file.write_text("def func(): pass")  # Missing docstring

            # Split the variant to handle space-separated arguments
            args: list[str] = true_variant.split()
            result: Result = self.runner.invoke(app, ["check"] + args + [str(temp_path)])

            # Should find issues in subdirectory (recursive=true)
            assert result.exit_code == 1, f"Failed for variant: {true_variant}"

    @parameterized.expand(
        input=[
            "--recursive=false",
            "--recursive=f",
            "--recursive=no",
            "--recursive=n",
            "--recursive=0",
            "--recursive=off",
            "--recursive false",
            "--recursive f",
            "--recursive no",
            "--recursive n",
            "--recursive 0",
            "--recursive off",
            "--recursive=FALSE",
            "--recursive=False",
            "--recursive=NO",
            "--recursive=No",
            "-r false",
            "-r f",
            "-r no",
            "-r n",
            "-r 0",
            "-r off",
            "-r F",
        ],
        name_func=name_func_flat_list,
    )
    def test_17_recursive_option_false_variants(self, false_variant: str) -> None:
        """
        Test that various 'false' values work for --recursive option.
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create subdirectory with Python file that has docstring issues
            subdir: Path = temp_path / "subdir"
            subdir.mkdir()
            py_file: Path = subdir / "test.py"
            py_file.write_text("def func(): pass")  # Missing docstring

            # Split the variant to handle space-separated arguments
            args: list[str] = false_variant.split()
            result: Result = self.runner.invoke(app, ["check"] + args + [str(temp_path)])

            # Should succeed because it doesn't check subdirectories (recursive=false)
            assert result.exit_code == 0, f"Failed for variant: false_{false_variant}"

    def test_18_recursive_option_default_behavior(self) -> None:
        """
        Test that --recursive defaults to true when no value is provided.
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create subdirectory with Python file that has docstring issues
            subdir: Path = temp_path / "subdir"
            subdir.mkdir()
            py_file: Path = subdir / "test.py"
            py_file.write_text("def func(): pass")  # Missing docstring

            # Test default behavior (should be recursive=true)
            result: Result = self.runner.invoke(app, ["check", str(temp_path)])

            # Should find issues in subdirectory (default recursive=true)
            assert result.exit_code == 1

    @parameterized.expand(
        input=[
            "--recursive=invalid",
            "--recursive=maybe",
            "--recursive=2",
            "-r bad",
            "--recursive xyz",
        ],
        name_func=name_func_flat_list,
    )
    def test_19_recursive_option_invalid_values(self, invalid_variant: str) -> None:
        """
        Test that invalid values for --recursive option raise appropriate errors.
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:

            f.write("def func(): pass")
            f.flush()

            try:

                # Split the variant to handle space-separated arguments
                args: list[str] = invalid_variant.split()
                result: Result = self.runner.invoke(app, ["check"] + args + [f.name])

                # Should fail with appropriate error message
                assert result.exit_code == 2, f"Should fail for invalid variant: {invalid_variant}"
                assert "Invalid boolean value" in result.output, f"Should show error for: {invalid_variant}"

            finally:

                Path(f.name).unlink()
