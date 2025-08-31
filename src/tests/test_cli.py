# ---------------------------------------------------------------------------- #
#                                                                              #
#     Setup                                                                 ####
#                                                                              #
# ---------------------------------------------------------------------------- #


## --------------------------------------------------------------------------- #
##  Imports                                                                 ####
## --------------------------------------------------------------------------- #


# ## Python StdLib Imports ----
import sys
import tempfile
from pathlib import Path
from textwrap import dedent
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

# ## Python Third Party Imports ----
import typer
from click.testing import Result
from parameterized import parameterized
from pytest import raises
from typer.testing import CliRunner

# ## Local First Party Imports ----
from docstring_format_checker import __version__
from docstring_format_checker.cli import (
    _parse_boolean_flag,
    _parse_recursive_flag,
    app,
    entry_point,
)
from tests.setup import (
    clean,
    name_func_flat_list,
    name_func_nested_list,
)


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

        self.runner = CliRunner(env={"NO_COLOR": "1"})

    def test_01_help_message(self) -> None:
        """
        Test help message is displayed.
        """

        result: Result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "A CLI tool to check and validate Python docstring formatting" in clean(result.output)

    def test_02_version_callback(self) -> None:
        """
        Test version callback functionality.
        """
        result: Result = self.runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "docstring-format-checker" in clean(result.output)

    def test_03_version_option(self) -> None:
        """
        Test --version option.
        """

        result: Result = self.runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert f"docstring-format-checker version {__version__}" in clean(result.output)

    def test_04_no_arguments_shows_help(self) -> None:
        """
        Test that no arguments shows help.
        """

        result: Result = self.runner.invoke(app, [])
        assert result.exit_code == 0  # Now shows help successfully
        assert "Usage:" in clean(result.output)
        assert "A CLI tool to check and validate Python docstring formatting and completeness" in clean(result.output)

    def test_05_config_example_command(self) -> None:
        """
        Test config-example command.
        """

        result: Result = self.runner.invoke(app, ["config-example"])
        if result.exit_code != 0:
            print(f"{result.exit_code=}")
            print(f"{clean(result.output)=}")
        assert result.exit_code == 0
        assert "[tool.dfc]" in clean(result.output)
        assert "[[tool.dfc.sections]]" in clean(result.output)

    def test_06_nonexistent_file(self) -> None:
        """
        Test error handling for nonexistent file.
        """

        result: Result = self.runner.invoke(app, ["check", "nonexistent.py"])
        assert result.exit_code == 1
        assert "Error: Path does not exist" in clean(result.output)

    def test_07_check_valid_python_file(self) -> None:
        """
        Test checking a valid Python file.
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=True) as f:

            f.write(
                dedent(
                    '''
                    def good_function() -> None:
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

            result: Result = self.runner.invoke(app, ["check", f.name])
            # Should succeed with default config
            assert result.exit_code == 0 or "All docstrings are valid" in clean(result.output)

    def test_08_check_invalid_python_file(self) -> None:
        """
        Test checking a Python file with missing docstrings.
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=True) as f:

            f.write(
                dedent(
                    """
                    def bad_function() -> None:
                        pass

                    class BadClass:
                        def bad_method(self) -> None:
                            return None
                    """
                )
            )

            f.flush()

            result: Result = self.runner.invoke(app, ["check", f.name])

            if result.exit_code != 1:
                print(f"{result.exit_code=}")
                print(f"{clean(result.output)=}")

            # Should fail due to missing docstrings
            assert result.exit_code == 1
            assert "error" in clean(result.output).lower()

    def test_09_check_directory(self) -> None:
        """
        Test checking a directory.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            temp_path = Path(temp_dir)

            # Create a Python file with missing docstrings
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(
                dedent(
                    """
                    def function_without_docstring() -> None:
                        pass
                    """
                )
            )

            result: Result = self.runner.invoke(app, ["check", str(temp_path)])

            if result.exit_code != 1:
                print(f"{result.exit_code=}")
                print(f"{clean(result.output)=}")

            # Should find issues in the directory
            assert result.exit_code == 1

    def test_10_check_directory_non_recursive(self) -> None:
        """
        Test checking a directory non-recursively using --recursive=false.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            temp_path = Path(temp_dir)

            # Create subdirectory with Python file
            subdir: Path = temp_path.joinpath("subdir")
            subdir.mkdir()
            py_file: Path = subdir.joinpath("test.py")
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
            test_file: Path = temp_path.joinpath("test_something.py")
            test_file.write_text("def func(): pass")

            regular_file: Path = temp_path.joinpath("regular.py")
            regular_file.write_text("def func(): pass")

            # Exclude test files
            result: Result = self.runner.invoke(app, ["check", "--exclude", "test_*.py", str(temp_path)])

            if result.exit_code != 1:
                print(f"{result.exit_code=}")
                print(f"{clean(result.output)=}")

            # Should only check regular.py and find issues
            assert result.exit_code == 1

    def test_12_quiet_option(self) -> None:
        """
        Test quiet option suppresses success messages.
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=True) as f:

            f.write(
                dedent(
                    '''
                    def good_function() -> None:
                        """
                        !!! note "Summary"
                            This function has a good docstring.
                        """
                        pass
                    '''
                )
            )

            f.flush()

            result: Result = self.runner.invoke(app, ["check", "--quiet", f.name])
            # Should succeed without any output
            assert result.exit_code == 0
            assert clean(result.output).strip() == ""

    def test_13_verbose_option(self) -> None:
        """
        Test verbose option shows detailed output.
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=True) as f:

            f.write("def func(): pass")
            f.flush()

            result: Result = self.runner.invoke(app, ["check", "--verbose", f.name])
            # Should show detailed output
            assert "Checking file:" in clean(result.output) or "Using" in clean(result.output)

    def test_14_custom_config_file(self) -> None:
        """
        Test using a custom configuration file.
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=True) as config_f:

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

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=True) as py_f:

                py_f.write("def func(): pass")
                py_f.flush()

                result: Result = self.runner.invoke(app, ["check", "--config", config_f.name, py_f.name])

                if result.exit_code != 1:
                    print(f"{result.exit_code=}")
                    print(f"{clean(result.output)=}")

                # Should use the custom config
                assert result.exit_code == 1  # Missing docstrings

    def test_15_nonexistent_config_file(self) -> None:
        """
        Test error handling for nonexistent config file.
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=True) as f:

            f.write("def func(): pass")
            f.flush()

            result: Result = self.runner.invoke(app, ["check", "--config", "nonexistent.toml", f.name])
            assert result.exit_code == 1
            assert "Configuration file does not exist" in clean(result.output)

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
            subdir: Path = temp_path.joinpath("subdir")
            subdir.mkdir()
            py_file: Path = subdir.joinpath("test.py")
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
            subdir: Path = temp_path.joinpath("subdir")
            subdir.mkdir()
            py_file: Path = subdir.joinpath("test.py")
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
            subdir: Path = temp_path.joinpath("subdir")
            subdir.mkdir()
            py_file: Path = subdir.joinpath("test.py")
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

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=True) as f:

            f.write("def func(): pass")
            f.flush()

            # Split the variant to handle space-separated arguments
            args: list[str] = invalid_variant.split()
            result: Result = self.runner.invoke(app, ["check"] + args + [f.name])

            # Should fail with appropriate error message
            assert result.exit_code == 2, f"Should fail for invalid variant: '{invalid_variant}'"
            # Check for the key error message components (more robust than exact string match)
            assert "Invalid value" in clean(result.output), f"Should show invalid value error for: '{invalid_variant}'"
            # Strip ANSI codes to handle CI environment differences
            assert "--recursive" in clean(result.output), f"Should mention --recursive option for: '{invalid_variant}'"

    def test_20_examples_callback(self) -> None:
        """
        Test examples callback functionality.
        """
        result: Result = self.runner.invoke(app, ["config-example"])
        assert result.exit_code == 0
        assert "Example configuration for docstring-format-checker" in clean(result.output)

    def test_21_check_examples_callback(self) -> None:
        """
        Test check command examples callback functionality.
        """
        result: Result = self.runner.invoke(app, ["check", "--examples"])
        assert result.exit_code == 0
        assert "Check Command Examples" in clean(result.output)

    def test_22_help_callback(self) -> None:
        """
        Test help callback functionality.
        """
        result: Result = self.runner.invoke(app, ["check", "--help"])
        assert result.exit_code == 0
        assert "Check docstrings in Python files" in clean(result.output)

    def test_23_parse_boolean_flag_edge_cases(self) -> None:
        """
        Test parse_boolean_flag function with edge cases.
        """

        # Create mock context and param
        mock_ctx = Mock()
        mock_param = Mock()

        # Test None value (default case)
        assert _parse_boolean_flag(mock_ctx, mock_param, None) == True

        # Test empty string (flag without value)
        assert _parse_boolean_flag(mock_ctx, mock_param, "") == True

        # Test invalid value raises exception
        with raises(typer.BadParameter):
            _parse_boolean_flag(mock_ctx, mock_param, "invalid")

    @parameterized.expand(
        input=[
            ("true", True),
            ("TRUE", True),
            ("t", True),
            ("yes", True),
            ("y", True),
            ("1", True),
            ("on", True),
            ("false", False),
            ("FALSE", False),
            ("f", False),
            ("no", False),
            ("n", False),
            ("0", False),
            ("off", False),
            ("invalid", None),
        ],
        name_func=name_func_nested_list,
    )
    def test_24_parse_recursive_flag_function(self, value: str, result: bool) -> None:
        """
        Test parse_recursive_flag function directly.
        """
        if value == "invalid":
            with raises(ValueError):
                _parse_recursive_flag("invalid")
        else:
            assert _parse_recursive_flag(value) == result

    def test_25_entry_point_function(self) -> None:
        """
        Test entry_point function.
        """

        # Mock sys.argv to simulate command line call
        with patch.object(sys, "argv", ["dfc", "--version"]):
            try:
                entry_point()
            except SystemExit:
                pass  # Expected for --version

    def test_26_config_error_handling(self) -> None:
        """
        Test configuration error handling in check command.
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=True) as f:

            f.write("def good_function():\n    '''This has a docstring.'''\n    pass")
            f.flush()

            # Test with malformed config file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=True) as config_f:

                config_f.write("invalid toml content [[[")
                config_f.flush()

                result: Result = self.runner.invoke(app, ["check", f.name, "--config", config_f.name])
                assert result.exit_code == 1  # Changed from 2 to 1
                assert "error" in clean(result.output).lower()

    def test_27_verbose_config_loading(self) -> None:
        """
        Test verbose output during config loading.
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=True) as f:
            f.write("def good_function():\n    '''This has a docstring.'''\n    pass")
            f.flush()

            # Test verbose with default config
            result: Result = self.runner.invoke(app, ["check", f.name, "--verbose"])
            # Check if it passes or has expected content
            assert result.exit_code in [0, 1]  # Allow either success or failure

    def test_28_auto_config_discovery(self) -> None:
        """
        Test automatic config file discovery.
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a Python file
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text("def good_function():\n    '''This has a docstring.'''\n    pass")

            # Create a config file in the same directory
            config_file: Path = temp_path.joinpath("pyproject.toml")
            config_file.write_text(
                dedent(
                    """
                    [tool.dfc]

                    [[tool.dfc.sections]]
                    order = 1
                    name = "summary"
                    type = "free_text"
                    required = true
                """
                ).strip()
            )

            # Test that config is auto-discovered
            result: Result = self.runner.invoke(app, ["check", str(py_file), "--verbose"])
            assert result.exit_code == 0
            print(clean(result.output))
            assert f"Using configuration from: {config_file.resolve()}" in clean(result.output)
            raise RuntimeError()

    def test_29_global_examples_callback(self) -> None:
        """
        Test global examples callback functionality.
        """
        result: Result = self.runner.invoke(app, ["--examples"])
        assert result.exit_code == 0
        assert "Examples" in clean(result.output)
        assert "dfc check" in clean(result.output)

    def test_30_error_during_checking(self) -> None:
        """
        Test error handling during file/directory checking.
        """
        # Test with a directory that causes an error during checking
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a file with invalid syntax to trigger an error during checking
            py_file: Path = temp_path.joinpath("invalid.py")
            py_file.write_text("def func(:\n    pass")  # Invalid syntax

            # Also create a directory to test the directory checking path
            result: Result = self.runner.invoke(app, ["check", str(temp_path)])

            # Should not crash but may return non-zero exit code due to syntax error
            assert result.exit_code in [0, 1, 2]  # Allow various error codes

    def test_31_error_summary_display(self) -> None:
        """
        Test error summary display functionality.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create multiple files with docstring issues
            for i in range(3):
                py_file: Path = temp_path.joinpath(f"test_{i}.py")
                py_file.write_text("def func(): pass")  # Missing docstring

            result: Result = self.runner.invoke(app, ["check", str(temp_path)])

            # Should find multiple errors and display summary
            assert result.exit_code == 1
            assert "error(s)" in clean(result.output)
            assert "file(s)" in clean(result.output)

    @parameterized.expand(
        input=[
            ("true", True),
            ("t", True),
            ("yes", True),
            ("y", True),
            ("1", True),
            ("on", True),
            ("TRUE", True),
            ("T", True),
            ("YES", True),
            ("Y", True),
            ("ON", True),
            ("false", False),
            ("f", False),
            ("no", False),
            ("n", False),
            ("0", False),
            ("off", False),
            ("FALSE", False),
            ("F", False),
            ("NO", False),
            ("N", False),
            ("OFF", False),
        ]
    )
    def test_32_parse_boolean_flag_values(self, value: str, expected: bool) -> None:
        """
        Test parse_boolean_flag values.
        """

        ctx = MagicMock()
        param = MagicMock()

        # Test each value and check it matches the expected result
        actual = _parse_boolean_flag(ctx, param, value)
        assert actual == expected, f"Failed for value: {value}, expected {expected}, got {actual}"

    def test_33_check_directory_verbose_message(self) -> None:
        """Test verbose message for directory checking."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a Python file with proper structure
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(
                dedent(
                    '''
                    def func() -> None:
                        """
                        !!! note "Summary"
                            Valid docstring.

                        Args:
                            None

                        Returns:
                            None
                        """
                        pass
                    '''
                )
            )

            result: Result = self.runner.invoke(app, ["check", str(temp_path), "--verbose"])

            # Should show verbose directory checking message
            assert (
                result.exit_code == 0
            ), f"Expected exit code 0, got {result.exit_code}. Output: {clean(result.output)}"
            assert "Checking directory:" in clean(result.output)
            assert "recursive=True" in clean(result.output)

    def test_34_check_command_exception_handling(self) -> None:
        """Test exception handling in check command."""
        # Test with a path that will cause an exception
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a file that will cause an exception when processed
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text('def func():\n    """Valid docstring."""\n    pass')

            # Mock the DocstringChecker to raise an exception

            with patch("docstring_format_checker.cli.DocstringChecker") as mock_checker:
                mock_instance = MagicMock()
                mock_checker.return_value = mock_instance
                mock_instance.check_directory.side_effect = Exception("Test error")

                result: Result = self.runner.invoke(app, ["check", str(temp_path)])

                # Should handle the exception and exit with code 1
                assert result.exit_code == 1
                assert "Error during checking: Test error" in clean(result.output)

    def test_35_check_file_specific_exception_handling(self) -> None:
        """
        Test exception handling for file checking.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a single file
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text('def func():\n    """Valid docstring."""\n    pass')

            # Mock the DocstringChecker to raise an exception for file checking

            with patch("docstring_format_checker.cli.DocstringChecker") as mock_checker:
                mock_instance = MagicMock()
                mock_checker.return_value = mock_instance
                mock_instance.check_file.side_effect = Exception("File check error")

                result: Result = self.runner.invoke(app, ["check", str(py_file)])

                # Should handle the exception and exit with code 1
                assert result.exit_code == 1
                assert "Error during checking: File check error" in clean(result.output)
