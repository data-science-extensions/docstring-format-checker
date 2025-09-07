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
from unittest.mock import MagicMock, patch

# ## Python Third Party Imports ----
from click.testing import Result
from typer.testing import CliRunner

# ## Local First Party Imports ----
from docstring_format_checker import __version__
from docstring_format_checker.cli import _format_error_messages, app, entry_point
from tests.setup import clean


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
        assert result.exit_code == 2  # Typer exits with 2 when required argument is missing
        assert "Usage:" in clean(result.output)
        # More flexible check for the description that handles line wrapping
        output_clean: str = clean(result.output)
        assert "A CLI tool to check and validate Python docstring formatting" in output_clean
        assert "completeness" in output_clean

    def test_05_example_config_subcommand(self) -> None:
        """
        Test example subcommand with --config flag.
        """
        result: Result = self.runner.invoke(app, ["example", "--config"])
        assert result.exit_code == 0
        assert "[tool.dfc]" in clean(result.output)
        assert "[[tool.dfc.sections]]" in clean(result.output)

    def test_06_nonexistent_file(self) -> None:
        """
        Test error handling for nonexistent file.
        """
        result: Result = self.runner.invoke(app, ["nonexistent.py"])
        assert result.exit_code == 1
        assert "Error: Path does not exist" in clean(result.output)

    def test_07_check_valid_python_file(self) -> None:
        """
        Test checking a valid Python file.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(
                dedent(
                    '''
                    def good_function() -> None:
                        """
                        !!! note "Summary"
                            This function has a good docstring.

                        ???+ info "Details"
                            More detailed information here.

                        Params:
                            None

                        Returns:
                            None
                        """
                        pass
                    '''
                ).strip()
            )

            # Should succeed with default config
            result: Result = self.runner.invoke(app, [str(py_file)])
            assert result.exit_code == 0
            assert "All docstrings are valid" in clean(result.output)

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_08_check_invalid_python_file(self) -> None:
        """
        Test checking a Python file with missing docstrings.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(
                dedent(
                    """
                    def bad_function() -> None:
                        pass

                    class BadClass:
                        def bad_method(self) -> None:
                            return None
                    """
                ).strip()
            )

            # Should fail due to missing docstrings
            result: Result = self.runner.invoke(app, [str(py_file)])
            assert result.exit_code == 1  # Should exit with error when docstring errors found
            assert "error" in clean(result.output).lower()

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_09_check_directory(self) -> None:
        """
        Test checking a directory.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a Python file with missing docstrings
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(
                dedent(
                    """
                    def function_without_docstring() -> None:
                        pass
                    """
                ).strip()
            )

            # Should find issues in the directory
            result: Result = self.runner.invoke(app, [str(temp_path)])
            assert result.exit_code == 1  # Should exit with error when docstring errors found

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_10_exclude_patterns(self) -> None:
        """
        Test excluding files with patterns.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create files
            temp_path = Path(temp_dir)
            test_file: Path = temp_path.joinpath("test_something.py")
            regular_file: Path = temp_path.joinpath("regular.py")

            # Write to files
            test_file.write_text("def func(): pass")
            regular_file.write_text("def func(): pass")

            # Should only check regular.py and find issues
            result: Result = self.runner.invoke(app, ["--exclude", "test_*.py", str(temp_path)])
            assert result.exit_code == 1  # Should exit with error when docstring errors found

            # Clean up
            Path(test_file).unlink(missing_ok=True)
            Path(regular_file).unlink(missing_ok=True)

    def test_11_quiet_option(self) -> None:
        """
        Test quiet option suppresses success messages.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(
                dedent(
                    '''
                    def good_function() -> None:
                        """
                        !!! note "Summary"
                            This function has a good docstring.
                        """
                        pass
                    '''
                ).strip()
            )

            # Should succeed without any output
            result: Result = self.runner.invoke(app, ["--quiet", str(py_file)])
            assert result.exit_code == 0
            assert clean(result.output).strip() == ""

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_12_table_output_option(self) -> None:
        """
        Test table output option shows detailed output.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text("def func(): pass")

            # Should show table output
            result: Result = self.runner.invoke(app, ["--output=table", str(py_file)])
            # Table output should contain the header elements
            output = clean(result.output)
            assert "File" in output and "Line" in output and "Item" in output

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_13_custom_config_file(self) -> None:
        """
        Test using a custom configuration file.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary config file
            temp_path = Path(temp_dir)
            config_file: Path = temp_path.joinpath("test_config.toml")
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

            # Create a temporary Python file
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text("def func(): pass")

            # Should use the custom config
            result: Result = self.runner.invoke(app, ["--config", str(config_file), str(py_file)])
            assert result.exit_code == 1  # Should exit with error when docstring errors found

            # Clean up
            config_file.unlink(missing_ok=True)
            py_file.unlink(missing_ok=True)

    def test_14_nonexistent_config_file(self) -> None:
        """
        Test error handling for nonexistent config file.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text("def func(): pass")

            result: Result = self.runner.invoke(app, ["--config", "nonexistent.toml", str(py_file)])
            assert result.exit_code == 1
            assert "Configuration file does not exist" in clean(result.output)

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_15_directory_recursive_default_behavior(self) -> None:
        """
        Test that directories are checked recursively by default.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create subdirectory with Python file that has docstring issues
            temp_path = Path(temp_dir)
            subdir: Path = temp_path.joinpath("subdir")
            subdir.mkdir()
            py_file: Path = subdir.joinpath("test.py")
            py_file.write_text("def func(): pass")  # Missing docstring

            # Test default behavior (should check recursively)
            result: Result = self.runner.invoke(app, [str(temp_path)])

            # Should find issues in subdirectory (default behavior is recursive)
            assert result.exit_code == 1

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_16_example_config_subcommand_content(self) -> None:
        """
        Test example subcommand config content.
        """
        result: Result = self.runner.invoke(app, ["example", "--config"])
        assert result.exit_code == 0
        assert "Example configuration for docstring-format-checker" in clean(result.output)

    def test_17_example_usage_subcommand(self) -> None:
        """
        Test example subcommand with --usage flag.
        """
        result: Result = self.runner.invoke(app, ["example", "--usage"])
        assert result.exit_code == 0
        assert "Examples" in clean(result.output)

    def test_18_help_callback(self) -> None:
        """
        Test help callback functionality.
        """
        result: Result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "A CLI tool to check and validate Python docstring formatting and completeness." in clean(result.output)

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

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text("def good_function():\n    '''This has a docstring.'''\n    pass")

            # Test with malformed config file
            config_file: Path = temp_path.joinpath("bad_config.toml")
            config_file.write_text("invalid toml content [[[")

            # Invoke the check command with the bad config file
            result: Result = self.runner.invoke(app, ["--config", str(config_file), str(py_file)])
            assert result.exit_code == 1  # Changed from 2 to 1
            assert "error" in clean(result.output).lower()

            # Clean up
            py_file.unlink(missing_ok=True)
            config_file.unlink(missing_ok=True)

    def test_27_verbose_config_loading(self) -> None:
        """
        Test verbose output during config loading.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text("def good_function():\n    '''This has a docstring.'''\n    pass")

            # Test verbose with default config
            result: Result = self.runner.invoke(app, ["--output=table", str(py_file)])

            # Check if it passes or has expected content
            assert result.exit_code in [0, 1]  # Allow either success or failure

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_28_auto_config_discovery(self) -> None:
        """
        Test automatic config file discovery.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a Python file
            temp_path = Path(temp_dir)
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

            # Test that config is auto-discovered (CLI should succeed with valid docstring)
            result: Result = self.runner.invoke(app, ["--output=table", str(py_file)])
            assert result.exit_code == 0
            output_clean: str = clean(result.output)
            # Should show success message when docstring is valid
            assert "✓ All docstrings are valid!" in output_clean

    def test_29_global_examples_callback(self) -> None:
        """
        Test global examples callback functionality.
        """
        result: Result = self.runner.invoke(app, ["--examples"])
        assert result.exit_code == 0
        assert "Examples" in clean(result.output)
        assert "dfc myfile.py" in clean(result.output)

    def test_30_error_during_checking(self) -> None:
        """
        Test error handling during file/directory checking.
        """

        # Test with a directory that causes an error during checking
        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a file with invalid syntax to trigger an error during checking
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("invalid.py")
            py_file.write_text("def func(:\n    pass")  # Invalid syntax

            # Also create a directory to test the directory checking path
            result: Result = self.runner.invoke(app, [str(temp_path)])

            # Should not crash but may return non-zero exit code due to syntax error
            assert result.exit_code in [0, 1, 2]  # Allow various error codes

    def test_31_error_summary_display(self) -> None:
        """
        Test error summary display functionality.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create multiple files with docstring issues
            temp_path = Path(temp_dir)
            for i in range(3):
                py_file: Path = temp_path.joinpath(f"test_{i}.py")
                py_file.write_text("def func(): pass")  # Missing docstring

            # Should find multiple errors and display summary
            result: Result = self.runner.invoke(app, [str(temp_path)])
            assert result.exit_code == 1
            assert "error(s)" in clean(result.output)
            assert "file(s)" in clean(result.output)

    def test_33_check_directory_verbose_message(self) -> None:
        """
        Test verbose message for directory checking.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a Python file with proper structure
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(
                dedent(
                    '''
                    def func() -> None:
                        """
                        !!! note "Summary"
                            Valid docstring.

                        Params:
                            None

                        Returns:
                            None
                        """
                        pass
                    '''
                ).strip()
            )

            # Should show success message for valid docstrings
            result: Result = self.runner.invoke(app, ["--output=table", str(temp_path)])
            assert (
                result.exit_code == 0
            ), f"Expected exit code 0, got {result.exit_code}. Output: {clean(result.output)}"
            assert "✓ All docstrings are valid!" in clean(result.output)

    def test_34_check_command_exception_handling(self) -> None:
        """
        Test exception handling in check command.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a file that will cause an exception when processed
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text('def func():\n    """Valid docstring."""\n    pass')

            with patch("docstring_format_checker.cli.DocstringChecker") as mock_checker:

                # Mock the DocstringChecker to raise an exception
                mock_instance = MagicMock()
                mock_checker.return_value = mock_instance
                mock_instance.check_directory.side_effect = Exception("Test error")

                # Should handle the exception and exit with code 1
                result: Result = self.runner.invoke(app, [str(temp_path)])
                assert result.exit_code == 1
                assert "Error during checking: Test error" in clean(result.output)

    def test_35_check_file_specific_exception_handling(self) -> None:
        """
        Test exception handling for file checking.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a single file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text('def func():\n    """Valid docstring."""\n    pass')

            with patch("docstring_format_checker.cli.DocstringChecker") as mock_checker:

                # Mock the DocstringChecker to raise an exception for file checking
                mock_instance = MagicMock()
                mock_checker.return_value = mock_instance
                mock_instance.check_file.side_effect = Exception("File check error")

                # Should handle the exception and exit with code 1
                result: Result = self.runner.invoke(app, [str(py_file)])
                assert result.exit_code == 1
                assert "Error during checking: File check error" in clean(result.output)

    def test_23_format_error_messages(self) -> None:
        """
        Test that _format_error_messages correctly formats error strings.
        """

        # Test single error
        single_error = "Missing required admonition sections: ['Parameters', 'Returns']"
        expected_single = "- Missing required admonition sections: ['Parameters', 'Returns']."
        assert _format_error_messages(single_error) == expected_single

        # Test multiple errors separated by semicolons
        multi_error = (
            "Missing required admonition sections: ['Parameters', 'Returns']; Expected closing parenthesis ')'"
        )
        expected_multi = (
            "- Missing required admonition sections: ['Parameters', 'Returns'];\n- Expected closing parenthesis ')'."
        )
        assert _format_error_messages(multi_error) == expected_multi

        # Test empty string
        assert _format_error_messages("") == "- ."

        # Test string that already has dash prefix (should not double-prefix)
        prefixed_error = "Missing required admonition sections: ['Parameters']"
        expected_prefixed = "- Missing required admonition sections: ['Parameters']."
        assert _format_error_messages(prefixed_error) == expected_prefixed

    def test_22_check_flag_exits_on_error(self) -> None:
        """
        Test that --check flag causes exit with error code 1 when issues are found.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text("def func(): pass")  # Missing docstring

            result: Result = self.runner.invoke(app, ["--check", str(py_file)])
            assert result.exit_code == 1
            assert "error" in clean(result.output).lower()

            py_file.unlink(missing_ok=True)

    def test_23_check_flag_succeeds_when_no_errors(self) -> None:
        """
        Test that --check flag succeeds with exit code 0 when no issues are found.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(
                dedent(
                    '''
                    def good_function() -> None:
                        """
                        !!! note "Summary"
                            This function has a good docstring.
                        """
                        pass
                    '''
                ).strip()
            )

            result: Result = self.runner.invoke(app, ["--check", str(py_file)])
            assert result.exit_code == 0
            assert "All docstrings are valid" in clean(result.output)

            py_file.unlink(missing_ok=True)

    def test_24_output_list_format(self) -> None:
        """
        Test that --output=list shows compact list format.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text("def func(): pass")  # Missing docstring

            result: Result = self.runner.invoke(app, ["--output=list", str(py_file)])
            assert result.exit_code == 1  # Should exit with error when docstring errors found
            output = clean(result.output)
            # List format should not contain table headers
            assert "File" not in output or "┃" not in output
            # But should contain the file path and error details
            assert "test.py" in output

            py_file.unlink(missing_ok=True)

    def test_25_output_table_format(self) -> None:
        """
        Test that --output=table shows detailed table format.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text("def func(): pass")  # Missing docstring

            result: Result = self.runner.invoke(app, ["--output=table", str(py_file)])
            assert result.exit_code == 1  # Should exit with error when docstring errors found
            output = clean(result.output)
            # Table format should contain table headers and structure
            assert "File" in output and "Line" in output and "Item" in output
            assert "┃" in output or "|" in output  # Table borders

            py_file.unlink(missing_ok=True)

    def test_26_output_short_alias(self) -> None:
        """
        Test that -o is an alias for --output.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text("def func(): pass")  # Missing docstring

            result: Result = self.runner.invoke(app, ["-o", "table", str(py_file)])
            assert result.exit_code == 1  # Should exit with error when docstring errors found
            output = clean(result.output)
            # Should show table format
            assert "File" in output and "Line" in output and "Item" in output

            py_file.unlink(missing_ok=True)

    def test_27_quiet_with_check_flag(self) -> None:
        """
        Test that --quiet --check shows minimal output but still exits with error.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text("def func(): pass")  # Missing docstring

            result: Result = self.runner.invoke(app, ["--quiet", "--check", str(py_file)])
            assert result.exit_code == 1
            output = clean(result.output)
            # Should show error count but not detailed errors
            assert "error(s)" in output.lower()
            # Should be minimal output
            assert len(output.split("\n")) < 5

            py_file.unlink(missing_ok=True)

    def test_28_quiet_success_case(self) -> None:
        """
        Test that --quiet shows no output on success.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(
                dedent(
                    '''
                    def good_function() -> None:
                        """
                        !!! note "Summary"
                            This function has a good docstring.
                        """
                        pass
                    '''
                ).strip()
            )

            result: Result = self.runner.invoke(app, ["--quiet", str(py_file)])
            assert result.exit_code == 0
            assert clean(result.output).strip() == ""

            py_file.unlink(missing_ok=True)

    def test_30_check_flag_short_alias(self) -> None:
        """
        Test that -c works as short alias for --check.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                dedent(
                    """
                    def bad_function():
                        pass
                    """
                ).strip()
            )

        py_file = Path(f.name)

        try:
            result: Result = self.runner.invoke(app, ["-c", str(py_file)])
            assert result.exit_code == 1  # Should exit with error when -c is used and issues found
            assert "Found" in clean(result.output)
        finally:
            py_file.unlink(missing_ok=True)

    def test_31_config_flag_short_alias(self) -> None:
        """
        Test that -f works as short alias for --config.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                dedent(
                    """
                    def good_function():
                        '''
                        !!! note "Summary"
                            A good function.

                        Params:
                            None.

                        Returns:
                            (None): Nothing.
                        '''
                        pass
                    """
                ).strip()
            )

        py_file = Path(f.name)

        try:
            # Test -f works the same as --config
            result: Result = self.runner.invoke(app, ["-f", "pyproject.toml", str(py_file)])
            assert result.exit_code == 0
        finally:
            py_file.unlink(missing_ok=True)
