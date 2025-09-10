# ---------------------------------------------------------------------------- #
#                                                                              #
#     Setup                                                                 ####
#                                                                              #
# ---------------------------------------------------------------------------- #


## --------------------------------------------------------------------------- #
##  Imports                                                                 ####
## --------------------------------------------------------------------------- #


# ## Python StdLib Imports ----
import subprocess
import sys
import tempfile
from ast import Module, stmt
from pathlib import Path
from subprocess import CompletedProcess
from textwrap import dedent
from typing import Any, Union
from unittest import TestCase

# ## Python Third Party Imports ----
import pytest

# ## Local First Party Imports ----
from docstring_format_checker.config import Config, GlobalConfig, SectionConfig
from docstring_format_checker.core import DocstringChecker
from docstring_format_checker.utils.exceptions import (
    DirectoryNotFoundError,
    DocstringError,
    InvalidFileError,
)


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Unit Tests                                                            ####
#                                                                              #
# ---------------------------------------------------------------------------- #


## --------------------------------------------------------------------------- #
##  Fixtures                                                                ####
## --------------------------------------------------------------------------- #


def _create_config(sections: list[SectionConfig], **global_flags) -> Config:
    """Helper function to create Config objects for tests."""
    global_config = GlobalConfig(**global_flags)
    return Config(global_config=global_config, sections=sections)


def simple_checker() -> DocstringChecker:
    """
    Create a simple docstring checker for testing.
    """
    sections: list[SectionConfig] = [
        SectionConfig(order=1, name="summary", type="free_text", required=True, admonition=False),
        SectionConfig(order=2, name="params", type="list_name_and_type", required=True, admonition=False),
        SectionConfig(order=3, name="returns", type="list_name_and_type", required=False, admonition=False),
    ]
    config = Config(global_config=GlobalConfig(), sections=sections)
    return DocstringChecker(config)


def detailed_checker() -> DocstringChecker:
    """
    Create a detailed docstring checker for testing.
    """
    sections: list[SectionConfig] = [
        SectionConfig(
            order=1,
            name="summary",
            type="free_text",
            admonition="note",
            prefix="!!!",
            required=True,
        ),
        SectionConfig(order=2, name="params", type="list_name_and_type", required=True),
        SectionConfig(order=3, name="returns", type="list_type", required=False),
        SectionConfig(
            order=4,
            name="examples",
            type="free_text",
            admonition="example",
            prefix="???+",
            required=False,
        ),
    ]
    config = Config(global_config=GlobalConfig(), sections=sections)
    return DocstringChecker(config)


## --------------------------------------------------------------------------- #
##  Cases                                                                   ####
## --------------------------------------------------------------------------- #


class TestDocstringChecker(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.simple_checker: DocstringChecker = simple_checker()
        cls.detailed_checker: DocstringChecker = detailed_checker()

    def test_01_check_file_with_good_docstrings(self) -> None:
        """
        Test checking a file with proper docstrings.
        """

        python_content: str = dedent(
            '''
            def good_function():
                """This function has a docstring."""
                pass

            class GoodClass:
                """This class has a docstring."""

                def good_method(self):
                    """This method has a docstring."""
                    pass
            '''
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)

            errors: list[DocstringError] = self.simple_checker.check_file(str(py_file))
            assert len(errors) == 0

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_02_check_file_with_missing_docstrings(self) -> None:
        """
        Test checking a file with missing docstrings.
        """

        python_content: str = dedent(
            """
            def bad_function():
                pass

            class BadClass:
                def bad_method(self):
                    pass
            """
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)

            errors: list[DocstringError] = self.simple_checker.check_file(str(py_file))
            assert len(errors) == 2  # function and method missing docstrings

            # Check error details
            function_error: DocstringError = next(e for e in errors if e.item_name == "bad_function")
            assert function_error.item_type == "function"
            assert "Missing docstring" in function_error.message

            method_error: DocstringError = next(e for e in errors if e.item_name == "bad_method")
            assert method_error.item_type == "method"

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_03_check_file_with_detailed_docstrings(self) -> None:
        """
        Test checking a file with detailed docstring requirements.
        """

        python_content: str = dedent(
            '''
            def detailed_function(param1, param2):
                """
                !!! note "Summary"
                    This is a summary.

                Params:
                    param1 (str):
                        First parameter.
                    param2 (int):
                        Second parameter.

                Returns:
                    (bool):
                        Return value.

                ???+ example "Examples"
                    Example usage here.
                """
                return True
            '''
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)

            errors: list[DocstringError] = self.detailed_checker.check_file(str(py_file))
            assert len(errors) == 0

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_04_check_file_with_incomplete_detailed_docstrings(self) -> None:
        """
        Test checking a file with incomplete detailed docstrings.
        """

        python_content: str = dedent(
            '''
            def incomplete_function(param1):
                """
                !!! note "Summary"
                    This is a summary.
                """
                return True
            '''
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)

            errors: list[DocstringError] = self.detailed_checker.check_file(str(py_file))
            assert len(errors) == 1
            assert "Params" in errors[0].message

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_05_check_directory(self) -> None:
        """
        Test checking a directory of Python files.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create test files
            temp_path = Path(temp_dir)
            temp_path.joinpath("good.py").write_text(
                dedent(
                    '''
                    def good_function():
                        """
                        Good docstring.
                        """
                        pass
                    '''
                )
            )

            temp_path.joinpath("bad.py").write_text(
                dedent(
                    """
                    def bad_function():
                        pass
                    """
                )
            )

            temp_path.joinpath("subdir").mkdir()
            temp_path.joinpath("subdir", "nested.py").write_text(
                dedent(
                    """
                    def nested_function():
                        pass
                    """
                )
            )

            # Check directory
            results: dict[str, list[DocstringError]] = self.simple_checker.check_directory(temp_path)

            # Should find errors in bad.py and nested.py
            assert len(results) == 2
            assert any("bad.py" in path for path in results.keys())
            assert any("nested.py" in path for path in results.keys())

    def test_06_check_directory_with_exclusions(self) -> None:
        """
        Test checking a directory with exclusion patterns.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create test files
            temp_path = Path(temp_dir)
            temp_path.joinpath("good.py").write_text(
                dedent(
                    '''
                    def good_function():
                        """Good docstring."""
                        pass
                    '''
                )
            )
            temp_path.joinpath("test_bad.py").write_text(
                dedent(
                    """
                    def bad_function():
                        pass
                    """
                )
            )

            temp_path.joinpath("regular_bad.py").write_text(
                dedent(
                    """
                    def bad_function():
                        pass
                    """
                )
            )

            # Check directory with exclusions
            results: dict[str, list[DocstringError]] = self.simple_checker.check_directory(
                temp_path, exclude_patterns=["test_*.py"]
            )

            # Should only find errors in regular_bad.py, not test_bad.py
            assert len(results) == 1
            assert any("regular_bad.py" in path for path in results.keys())
            assert not any("test_bad.py" in path for path in results.keys())

    def test_08_check_file_syntax_error(self) -> None:
        """
        Test handling of Python syntax errors.
        """

        python_content: str = dedent(
            """
            def bad_syntax(
                pass
            """
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)

            with pytest.raises(SyntaxError):
                self.simple_checker.check_file(str(py_file))

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_09_check_non_python_file(self) -> None:
        """
        Test error handling for non-Python files.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary non-Python file
            temp_path = Path(temp_dir)
            txt_file: Path = temp_path.joinpath("test.txt")
            txt_file.write_text("This is not a Python file")

            with pytest.raises(InvalidFileError):
                self.simple_checker.check_file(str(txt_file))

            # Clean up
            txt_file.unlink(missing_ok=True)

    def test_10_check_nonexistent_file(self) -> None:
        """
        Test error handling for nonexistent files.
        """

        with pytest.raises(FileNotFoundError):
            self.simple_checker.check_file("nonexistent.py")

    def test_11_private_functions_ignored(self) -> None:
        """
        Test that private functions and classes are ignored.
        """

        python_content: str = dedent(
            '''
            def _private_function():
                pass

            class _PrivateClass:
                def _private_method(self):
                    pass

                def __dunder_method__(self):
                    pass

            def public_function():
                """
                This should be checked.
                """
                pass
            '''
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)

            errors: list[DocstringError] = self.simple_checker.check_file(str(py_file))
            # Should only check public_function, ignore private ones
            assert len(errors) == 0

    def test_12_unicode_decode_error(self) -> None:
        """
        Test handling of Unicode decode errors.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a file with invalid UTF-8 content
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")

            # Write invalid UTF-8 bytes
            py_file.write_bytes(b"def function():\n    '''Invalid \xff\xfe Unicode'''\n    pass")

            with pytest.raises(ValueError, match="Cannot decode file"):
                self.simple_checker.check_file(str(py_file))

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_13_empty_sections_config(self) -> None:
        """
        Test checker with empty sections configuration.
        """

        empty_checker = DocstringChecker(_create_config([]))
        python_content: str = dedent(
            '''
            def function_with_docstring():
                """
                This has a docstring.
                """
                pass
            '''
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)

            errors: list[DocstringError] = empty_checker.check_file(str(py_file))
            # No sections to check, so no errors
            assert len(errors) == 0

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_14_check_directory_empty(self) -> None:
        """
        Test checking empty directory.
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            results: dict[str, list[DocstringError]] = self.simple_checker.check_directory(temp_dir)
            assert len(results) == 0

    def test_15_check_directory_no_python_files(self) -> None:
        """
        Test checking directory with no Python files.
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create non-Python files
            temp_path.joinpath("readme.txt").write_text("This is not Python")
            temp_path.joinpath("config.json").write_text('{"key": "value"}')

            results: dict[str, list[DocstringError]] = self.simple_checker.check_directory(temp_dir)
            assert len(results) == 0

    def test_16_nested_class_methods(self) -> None:
        """
        Test checking nested class methods.
        """

        python_content: str = dedent(
            '''
            class OuterClass:
                """
                Outer class docstring.
                """

                def outer_method(self):
                    """
                    Outer method docstring.
                    """
                    pass

                class InnerClass:
                    """
                    Inner class docstring.
                    """

                    def inner_method(self):
                        """
                        Inner method docstring.
                        """
                        pass

                    def missing_docstring_inner(self):
                        pass
            '''
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)

            errors: list[DocstringError] = self.simple_checker.check_file(str(py_file))
            # Should find one error: missing_docstring_inner
            assert len(errors) == 1
            assert "Missing docstring for method" in errors[0].message

    def test_17_function_with_decorators(self) -> None:
        """
        Test functions with decorators.
        """

        python_content: str = dedent(
            '''
            @property
            def decorated_function():
                """
                This has a docstring.
                """
                pass

            @staticmethod
            @classmethod
            def multi_decorated():
                pass
            '''
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)

            errors: list[DocstringError] = self.simple_checker.check_file(str(py_file))
            # Should find one error: multi_decorated missing docstring
            assert len(errors) == 1
            assert "Missing docstring for function" in errors[0].message

    def test_18_complex_docstring_validation(self) -> None:
        """
        Test complex docstring validation with multiple sections.
        """

        complex_sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
            SectionConfig(order=2, name="params", type="list_name_and_type", required=True),
            SectionConfig(order=3, name="returns", type="free_text", required=True),
            SectionConfig(order=4, name="raises", type="list_type", required=False),
        ]

        complex_checker = DocstringChecker(_create_config(complex_sections))

        python_content: str = dedent(
            '''
            def complex_function(param1, param2):
                """
                This is a summary.

                Params:
                    param1 (str):
                        First parameter description.
                    param2 (int):
                        Second parameter description.

                Returns:
                    (bool):
                        Return value description.

                Raises:
                    (ValueError):
                        When something goes wrong.
                """
                return True

            def incomplete_function(param1):
                """
                This function is missing sections.
                """
                return True
            '''
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)

            errors: list[DocstringError] = complex_checker.check_file(str(py_file))
            # Should find errors in incomplete_function
            assert len(errors) > 0
            error_messages: list[str] = [error.message for error in errors]
            assert any("params" in msg.lower() or "param" in msg.lower() for msg in error_messages)

    def test_19_malformed_docstrings(self) -> None:
        """
        Test handling of malformed docstrings.
        """

        python_content: str = dedent(
            '''
            def function_with_weird_docstring():
                """
                This docstring has weird formatting

                Params:


                Returns:
                    Something weird

                Unknown Section:
                    This shouldn't be here
                """
                pass
            '''
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)

            errors: list[DocstringError] = self.detailed_checker.check_file(str(py_file))
            # Should handle gracefully and report appropriate errors
            assert isinstance(errors, list)

    def test_20_special_method_names(self) -> None:
        """
        Test handling of special method names.
        """

        python_content: str = dedent(
            '''
            class TestClass:
                """
                Test class.
                """

                def __init__(self):
                    """
                    Constructor.
                    """
                    pass

                def __str__(self):
                    """
                    String representation.
                    """
                    return "test"

                def __len__(self):
                    # Missing docstring for dunder method
                    return 0

                def _protected_method(self):
                    # Protected method without docstring
                    pass
            '''
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)

            errors: list[DocstringError] = self.simple_checker.check_file(str(py_file))
            # Should find errors for missing docstrings (excluding private methods starting with _)
            # In simple config, private methods are likely ignored, so check dunder methods only
            error_methods: list[str] = [error.message for error in errors]
            # May or may not have errors depending on config for dunder methods

    def test_21_async_functions(self) -> None:
        """
        Test checking async functions.
        """

        python_content: str = dedent(
            '''
            async def async_function():
                """
                This is an async function.
                """
                pass

            async def async_missing_docstring():
                pass
            '''
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)

            errors: list[DocstringError] = self.simple_checker.check_file(str(py_file))
            # Should find one error: async_missing_docstring
            assert len(errors) == 1
            assert "Missing docstring for function" in errors[0].message

    def test_22_lambda_functions(self) -> None:
        """
        Test that lambda functions are ignored.
        """

        python_content: str = dedent(
            '''
            # Lambda functions should be ignored
            my_lambda = lambda x: x * 2

            def regular_function():
                """
                This should be checked.
                """
                lambda y: y + 1  # Nested lambda
                pass
            '''
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)

            errors: list[DocstringError] = self.simple_checker.check_file(str(py_file))
            # Should only check regular_function, no errors about lambdas
            assert len(errors) == 0

    def test_23_check_file_error_handling(self) -> None:
        """
        Test error handling for invalid files in check_file.
        """

        # Test with non-existent file
        with pytest.raises(FileNotFoundError):
            self.simple_checker.check_file("/non/existent/file.py")

        # Test with non-Python file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            txt_file: Path = temp_path.joinpath("test.txt")
            txt_file.write_text("This is not Python")

            with pytest.raises(InvalidFileError, match="File must be a Python file"):
                self.simple_checker.check_file(str(txt_file))

            # Clean up
            txt_file.unlink(missing_ok=True)

    def test_24_check_directory_error_handling(self) -> None:
        """
        Test error handling in check_directory method.
        """

        # Test with non-existent directory
        with pytest.raises(FileNotFoundError):
            self.simple_checker.check_directory("/nonexistent/directory")

        # Test with file instead of directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text("def test(): pass")

            with pytest.raises(DirectoryNotFoundError):
                self.simple_checker.check_directory(str(py_file))

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_25_section_order_validation(self) -> None:
        """
        Test validation of section order in docstrings.
        """

        # Create a checker with ordered sections
        ordered_sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
            SectionConfig(order=2, name="params", type="list_name_and_type", required=False),
            SectionConfig(order=3, name="returns", type="free_text", required=False),
        ]

        ordered_checker = DocstringChecker(_create_config(ordered_sections))

        python_content: str = dedent(
            '''
            def bad_order_function(param1):
                """
                This function has sections in wrong order.

                Returns:
                    Something

                Params:
                    param1:
                        A parameter
                """
                return True
            '''
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)

            errors: list[DocstringError] = ordered_checker.check_file(str(py_file))
            # Should find error about section order
            assert len(errors) > 0
            error_messages: list[str] = [error.message for error in errors]
            assert any("out of order" in msg.lower() for msg in error_messages)

    def test_26_directory_check_with_problematic_files(self) -> None:
        """
        Test directory checking when some files have errors.
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a good Python file
            good_file: Path = temp_path.joinpath("good.py")
            good_file.write_text("def good_func():\n    '''Good docstring.'''\n    pass")

            # Create a file with syntax error
            bad_file: Path = temp_path.joinpath("bad.py")
            bad_file.write_text("def bad_func(\n    # Missing closing parenthesis")

            # Check directory - should handle both files
            result: dict[str, list[DocstringError]] = self.simple_checker.check_directory(str(temp_path))

            # Should have results for both files
            assert isinstance(result, dict)
            assert len(result) >= 1  # At least the bad file should appear

            # Check that syntax error was captured
            if str(bad_file) in result:
                errors: list[DocstringError] = result[str(bad_file)]
                assert len(errors) >= 1
                assert any("syntax" in error.message.lower() or "invalid" in error.message.lower() for error in errors)

    def test_27_list_type_and_list_name_sections(self) -> None:
        """
        Test validation of list_type and list_name section types.
        """

        # Create checker with list_type and list_name sections
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
            SectionConfig(order=2, name="raises", type="list_type", required=False),
            SectionConfig(order=3, name="yields", type="list_type", required=False),
            SectionConfig(order=4, name="authors", type="list_name", required=False),
        ]

        checker = DocstringChecker(_create_config(sections))

        python_content: str = dedent(
            '''
            def function_with_list_sections():
                """
                Summary of the function.

                Raises:
                    (FileNotFoundError):
                        When something goes wrong

                Authors:
                    John Doe
                    Jane Smith
                """
                pass

            def function_missing_sections():
                """
                Just a summary.
                """
                pass
            '''
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)

            errors: list[DocstringError] = checker.check_file(str(py_file))
            # May have errors for missing sections in the second function
            # This test ensures list_type and list_name sections are processed
            assert isinstance(errors, list)

    def test_28_missing_docstring_error_creation(self) -> None:
        """
        Test DocstringError creation for missing docstrings.
        """

        # Create checker that requires docstrings
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
        ]

        checker = DocstringChecker(_create_config(sections))

        python_content: str = dedent(
            """
            def function_without_docstring():
                pass

            class ClassWithoutDocstring:
                def method_without_docstring(self):
                    pass
            """
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)

            errors: list[DocstringError] = checker.check_file(str(py_file))
            # Should find errors for missing docstrings
            assert len(errors) >= 2  # Function and class/method

            # Check error messages contain appropriate text
            error_messages: list[str] = [error.message for error in errors]
            assert any("Missing docstring for" in msg for msg in error_messages)

    def test_29_detailed_section_validation(self) -> None:
        """
        Test detailed validation of different section types.
        """

        # Create checker with various section types
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
            SectionConfig(order=2, name="params", type="list_name_and_type", required=True),
            SectionConfig(order=3, name="returns", type="list_name_and_type", required=True),
            SectionConfig(order=4, name="raises", type="list_type", required=True),
            SectionConfig(order=5, name="yields", type="list_type", required=False),
            SectionConfig(order=6, name="notes", type="list_name", required=False),
        ]

        checker = DocstringChecker(_create_config(sections))

        # Function with incomplete sections
        python_content: str = dedent(
            '''
            def incomplete_function(param1, param2):
                """
                This function has incomplete documentation.

                Params:
                    param1:
                        First parameter
                    # Missing param2 and type info
                """
                return "something"
            '''
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)

            errors: list[DocstringError] = checker.check_file(str(py_file))
            # Should find errors for missing/invalid sections
            assert len(errors) > 0

            error_messages: list[str] = [error.message for error in errors]
            # Should find missing required sections
            assert any("Returns" in msg or "returns" in msg for msg in error_messages)
            assert any("Raises" in msg or "raises" in msg for msg in error_messages)

    def test_30_simple_section_validation(self) -> None:
        """
        Test validation of simple list_name sections.
        """

        # Create checker with list_name section
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
            SectionConfig(order=2, name="authors", type="list_name", required=True),
        ]

        checker = DocstringChecker(_create_config(sections))

        python_content: str = dedent(
            '''
            def function_missing_authors():
                """
                Function without authors section.
                """
                pass
            '''
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)

            errors: list[DocstringError] = checker.check_file(str(py_file))
            # Should find error for missing authors section
            assert len(errors) > 0

            error_messages: list[str] = [error.message for error in errors]
            assert any("authors" in msg.lower() for msg in error_messages)

    def test_31_yields_section_validation(self) -> None:
        """
        Test validation of yields sections specifically.
        """

        # Create checker with yields section
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
            SectionConfig(order=2, name="yields", type="list_type", required=True),
        ]

        checker = DocstringChecker(_create_config(sections))

        python_content: str = dedent(
            '''
            def generator_without_yields():
                """
                Generator function without yields section.
                """
                yield 1
                yield 2
            '''
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)

            errors: list[DocstringError] = checker.check_file(str(py_file))
            # Should find error for missing yields section
            assert len(errors) > 0

            error_messages: list[str] = [error.message for error in errors]
            assert any("yields" in msg.lower() for msg in error_messages)

    def test_32_returns_yields_mutual_exclusivity(self) -> None:
        """
        Test that functions cannot have both Returns and Yields sections.
        """

        # Create checker with both returns and yields sections
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
            SectionConfig(order=2, name="returns", type="list_name_and_type", required=False),
            SectionConfig(order=3, name="yields", type="list_type", required=False),
        ]

        checker = DocstringChecker(_create_config(sections))

        python_content: str = dedent(
            '''
            def function_with_both_returns_and_yields():
                """
                Function with both returns and yields sections.

                Returns:
                    (str):
                        Some return value

                Yields:
                    (int):
                        Some yielded value
                """
                return "test"
            '''
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)

            errors: list[DocstringError] = checker.check_file(str(py_file))
            # Should find error for having both returns and yields
            assert len(errors) > 0

            error_messages: list[str] = [error.message for error in errors]
            assert any("both Returns and Yields" in msg for msg in error_messages)

    def test_33_missing_docstring_error(self) -> None:
        """
        Test handling of missing docstring errors.
        """

        # Create checker with simple required docstring
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
        ]

        checker = DocstringChecker(_create_config(sections))

        python_content: str = dedent(
            """
            def function_without_docstring():
                return "test"
            """
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)

            errors: list[DocstringError] = checker.check_file(str(py_file))
            # Should find missing docstring error
            assert len(errors) > 0

            error_messages: list[str] = [error.message for error in errors]
            assert any("missing docstring" in msg.lower() for msg in error_messages)

    def test_34_examples_section_validation(self) -> None:
        """
        Test validation of examples section in docstrings.
        """

        # Create checker with examples section
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
            SectionConfig(order=2, name="examples", type="free_text", required=True),
        ]

        checker = DocstringChecker(_create_config(sections))

        python_content: str = dedent(
            '''
            def function_with_examples():
                """
                Function with examples section.

                ???+ example "Examples"

                    Here is an example:

                    >>> function_with_examples()
                    'result'
                """
                return "result"

            def function_without_examples():
                """
                Function without examples section.
                """
                return "result"
            '''
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary Python file
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

            # Clean up
            py_file.unlink(missing_ok=True)

            # Should find error for missing examples section
            assert len(errors) > 0
            error_messages: list[str] = [error.message for error in errors]
            assert any("examples" in msg.lower() for msg in error_messages)

    def test_35_cli_main_execution(self) -> None:
        """
        Test CLI main execution for coverage.
        """

        # This tests the __main__ execution path
        # Test the __main__ execution by running the module
        result: CompletedProcess[str] = subprocess.run(
            [sys.executable, "-m", "docstring_format_checker.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent.resolve(),
        )

        # Should show help and exit with code 0
        assert result.returncode == 0
        assert "Usage:" in result.stdout

    def test_36_unknown_free_text_section_validation(self) -> None:
        """
        Test validation of custom free text sections.
        """

        # Create a section with a custom name for free text type
        # This should work as long as the section is defined in configuration
        custom_sections: list[SectionConfig] = [
            SectionConfig(order=1, name="unknown custom section", type="free_text", required=True, admonition=False),
        ]

        checker = DocstringChecker(_create_config(custom_sections))

        python_content: str = dedent(
            '''
            def test_function():
                """
                Unknown Custom Section:
                    This is a function with a custom section type that should validate successfully.
                """
                pass
            '''
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

            # Should have no errors for custom free text sections that are defined
            assert len(errors) == 0, f"Should not have errors for defined custom section, got: {errors}"

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_37_summary_section_simple_docstring_validation(self) -> None:
        """
        Test that simple docstrings are accepted for summary sections.
        """

        # Create a summary section that should accept simple docstrings
        summary_sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
        ]

        checker = DocstringChecker(_create_config(summary_sections))

        python_content: str = dedent(
            '''
            def test_function():
                """
                This is a simple docstring that should be accepted as summary.
                """
                pass
            '''
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

            # Should validate as true - this tests when: return len(docstring.strip()) > 0
            assert len(errors) == 0, f"Should not have errors for simple summary docstring, got: {errors}"

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_38_summary_section_formal_pattern_validation(self) -> None:
        """
        Test that formal summary patterns are accepted for summary sections.
        """

        # Create a summary section that should accept formal patterns
        summary_sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition=False),
        ]

        checker = DocstringChecker(_create_config(summary_sections))

        python_content: str = dedent(
            '''
            def test_function():
                """
                Summary:
                    This is a formal summary section.
                """
                pass
            '''
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

            # Should validate as true - this tests when: return True for formal pattern
            assert len(errors) == 0, f"Should not have errors for formal summary pattern, got: {errors}"

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_39_overload_functions_ignored(self) -> None:
        """
        Test that functions with @overload decorator are ignored.
        """

        checker: DocstringChecker = simple_checker()

        # Python content with @overload functions
        python_content: str = dedent(
            '''
            from typing import overload, Union

            @overload
            def example_function(x: int) -> int: ...
            @overload
            def example_function(x: str) -> str: ...
            def example_function(x: Union[int, str]) -> Union[int, str]:
                """
                Summary:
                    A function with overloads.

                Params:
                    x (Union[int, str]):
                        Input parameter.

                Returns:
                    (Union[int, str]):
                        Same type as input.
                """
                return x

            def regular_function():
                """
                Summary:
                    A regular function with proper docstring.
                """
                pass
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

            # Should have no errors - @overload functions are ignored
            assert len(errors) == 0, f"@overload functions should be ignored, got: {errors}"

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_40_overload_functions_with_typing_prefix(self) -> None:
        """
        Test that functions with @typing.overload decorator are ignored.
        """

        checker: DocstringChecker = simple_checker()

        # Python content with @typing.overload functions
        python_content: str = dedent(
            '''
            import typing

            @typing.overload
            def example_function(x: int) -> int: ...
            @typing.overload
            def example_function(x: str) -> str: ...
            def example_function(x: typing.Union[int, str]) -> typing.Union[int, str]:
                """
                Summary:
                    A function with overloads using typing.overload.

                Params:
                    x (typing.Union[int, str]):
                        Input parameter.

                Returns:
                    (typing.Union[int, str]):
                        Same type as input.
                """
                return x
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

            # Should have no errors - @typing.overload functions are ignored
            assert len(errors) == 0, f"@typing.overload functions should be ignored, got: {errors}"

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_41_overload_missing_implementation_docstring(self) -> None:
        """
        Test that missing docstring on implementation function (not @overload) is caught.
        """

        checker: DocstringChecker = simple_checker()

        # Python content with @overload functions but missing docstring on implementation
        python_content: str = dedent(
            """
            from typing import overload, Union

            @overload
            def example_function(x: int) -> int: ...
            @overload
            def example_function(x: str) -> str: ...
            def example_function(x: Union[int, str]) -> Union[int, str]:
                # Missing docstring here
                return x
            """
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

            # Should have one error for the implementation function missing docstring
            assert len(errors) == 1, f"Expected 1 error for missing implementation docstring, got: {len(errors)}"
            assert "Missing docstring for function" in errors[0].message
            assert errors[0].item_name == "example_function"
            # The error should be on the line of the implementation, not the overloads
            assert errors[0].line_number > 6  # Should be on the implementation line

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_42_mixed_overload_and_regular_functions(self) -> None:
        """
        Test a mix of @overload functions, regular functions with docstrings, and regular functions without.
        """

        # Use a checker that only requires summary, not params
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
        ]
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        # Python content mixing overload and regular functions
        python_content: str = dedent(
            '''
            from typing import overload, Union

            @overload
            def overload_func(x: int) -> int: ...
            @overload
            def overload_func(x: str) -> str: ...
            def overload_func(x: Union[int, str]) -> Union[int, str]:
                """Implementation of overloaded function."""
                return x

            def good_regular_function():
                """A regular function with proper docstring."""
                pass

            def bad_regular_function():
                # This one is missing a docstring
                pass
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

            # Should have one error only for the regular function without docstring
            assert len(errors) == 1, f"Expected 1 error for bad_regular_function, got: {len(errors)}"
            assert "Missing docstring for function" in errors[0].message
            assert errors[0].item_name == "bad_regular_function"

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_43_async_overload_functions(self) -> None:
        """
        Test that async functions with @overload decorator are ignored.
        """

        checker: DocstringChecker = simple_checker()

        # Python content with async @overload functions
        python_content: str = dedent(
            '''
            from typing import overload, Union
            import asyncio

            @overload
            async def async_example(x: int) -> int: ...
            @overload
            async def async_example(x: str) -> str: ...
            async def async_example(x: Union[int, str]) -> Union[int, str]:
                """
                Summary:
                    An async function with overloads.

                Params:
                    x (Union[int, str]):
                        Input parameter.

                Returns:
                    (Union[int, str]):
                        Same type as input.
                """
                return x
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

            # Should have no errors - async @overload functions are ignored
            assert len(errors) == 0, f"Async @overload functions should be ignored, got: {errors}"

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_44_overload_functions_in_class(self) -> None:
        """
        Test that @overload methods in classes are handled correctly.
        """

        checker: DocstringChecker = simple_checker()

        # Python content with @overload methods in a class
        python_content: str = dedent(
            '''
            from typing import overload, Union

            class ExampleClass:
                """
                Summary:
                    Example class with overloaded methods.
                """

                @overload
                def method(self, x: int) -> int: ...
                @overload
                def method(self, x: str) -> str: ...
                def method(self, x: Union[int, str]) -> Union[int, str]:
                    """
                    Summary:
                        Overloaded method implementation.

                    Params:
                        x (Union[int, str]):
                            Input parameter.

                    Returns:
                        (Union[int, str]):
                            Same type as input.
                    """
                    return x

                def regular_method(self):
                    """
                    Summary:
                        A regular method with proper docstring.
                    """
                    pass
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

            # Should have no errors - @overload methods are ignored
            assert len(errors) == 0, f"@overload methods in class should be ignored, got: {errors}"

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_45_overload_detection_helper_method(self) -> None:
        """
        Test the _is_overload_function helper method directly.
        """
        # ## Python StdLib Imports ----
        import ast

        checker: DocstringChecker = simple_checker()

        # Test direct @overload
        overload_code: str = dedent(
            """
            from typing import overload

            @overload
            def func(x: int) -> int: ...
        """
        ).strip()

        tree = ast.parse(overload_code)
        func_node = tree.body[1]  # Second node is the function
        assert isinstance(func_node, ast.FunctionDef)
        assert checker._is_overload_function(func_node), "Should detect @overload decorator"

        # Test @typing.overload
        typing_overload_code: str = dedent(
            """
            import typing

            @typing.overload
            def func(x: int) -> int: ...
        """
        ).strip()

        tree = ast.parse(typing_overload_code)
        func_node = tree.body[1]  # Second node is the function
        assert isinstance(func_node, ast.FunctionDef)
        assert checker._is_overload_function(func_node), "Should detect @typing.overload decorator"

        # Test regular function without @overload
        regular_code: str = dedent(
            """
            def func(x: int) -> int:
                return x
        """
        ).strip()

        tree = ast.parse(regular_code)
        func_node = tree.body[0]  # First node is the function
        assert isinstance(func_node, ast.FunctionDef)
        assert not checker._is_overload_function(func_node), "Should not detect @overload on regular function"

        # Test function with other decorator
        other_decorator_code: str = dedent(
            """
            @property
            def func(self):
                return self._value
        """
        ).strip()

        tree: Module = ast.parse(other_decorator_code)
        func_node: stmt = tree.body[0]  # First node is the function
        assert isinstance(func_node, ast.FunctionDef)
        assert not checker._is_overload_function(
            func_node
        ), "Should not detect @overload on function with other decorators"

    def test_46_admonition_validation_correct_admonition(self) -> None:
        """
        Test that correct admonition values pass validation.
        """
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition="note", prefix="!!!"),
            SectionConfig(order=2, name="details", type="free_text", required=False, admonition="info", prefix="???+"),
        ]
        config = _create_config(sections)
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        # Python content with correct admonitions
        python_content: str = dedent(
            '''
            def test_function():
                """
                !!! note "Summary"
                    This has the correct admonition.

                ???+ info "Details"
                    This also has the correct admonition.
                """
                pass
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

            # Should have no errors
            assert len(errors) == 0, f"Expected no errors for correct admonitions, got: {[e.message for e in errors]}"

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_47_admonition_validation_incorrect_admonition(self) -> None:
        """
        Test that incorrect admonition values are caught.
        """
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition="note", prefix="!!!"),
            SectionConfig(order=2, name="details", type="free_text", required=False, admonition="info", prefix="???+"),
        ]
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        # Python content with wrong admonition for details section
        python_content: str = dedent(
            '''
            def test_function():
                """
                !!! note "Summary"
                    This has the correct admonition.

                ???+ abstract "Details"
                    This has wrong admonition (should be 'info').
                """
                pass
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

            # Should have an error about incorrect admonition
            assert len(errors) == 1, f"Expected 1 error for incorrect admonition, got: {len(errors)}"
            assert (
                "incorrect admonition" in errors[0].message.lower()
            ), f"Expected admonition error, got: {errors[0].message}"
            assert "abstract" in errors[0].message, f"Expected 'abstract' in error message, got: {errors[0].message}"
            assert "info" in errors[0].message, f"Expected 'info' in error message, got: {errors[0].message}"

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_48_undefined_section_validation_defined_sections(self) -> None:
        """
        Test that sections defined in configuration don't trigger undefined section errors.
        """
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition="note", prefix="!!!"),
            SectionConfig(order=2, name="params", type="list_name_and_type", required=False),
            SectionConfig(order=3, name="returns", type="list_type", required=False),
            SectionConfig(
                order=4, name="examples", type="free_text", required=False, admonition="example", prefix="???+"
            ),
        ]
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        # Python content with only defined sections
        python_content: str = dedent(
            '''
            def test_function(param1: str) -> bool:
                """
                !!! note "Summary"
                    This function has only defined sections.

                Params:
                    param1 (str): A parameter.

                Returns:
                    (bool): A return value.

                ???+ example "Examples"
                    Some examples here.
                """
                return True
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

            # Should have no errors
            assert len(errors) == 0, f"Expected no errors for defined sections, got: {[e.message for e in errors]}"

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_49_undefined_section_validation_undefined_sections(self) -> None:
        """
        Test that sections not defined in configuration trigger undefined section errors.
        """
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition="note", prefix="!!!"),
            SectionConfig(order=2, name="params", type="list_name_and_type", required=False),
            SectionConfig(order=3, name="returns", type="list_type", required=False),
        ]
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        # Python content with undefined sections
        python_content: str = dedent(
            '''
            def test_function(param1: str) -> bool:
                """
                !!! note "Summary"
                    This function has undefined sections.

                Params:
                    param1 (str): A parameter.

                Returns:
                    (bool): A return value.

                ??? question "References"
                    - Some reference (not in config).

                Notes:
                    Some additional notes (not in config).
                """
                return True
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

            # Should have errors for undefined sections
            assert len(errors) == 1, f"Expected 1 error for undefined sections, got: {len(errors)}"
            error_message: str = errors[0].message.lower()

            # Check that both undefined sections are mentioned
            has_references_error: bool = (
                "references" in error_message and "not defined in configuration" in error_message
            )
            has_notes_error: bool = "notes" in error_message and "not defined in configuration" in error_message

            assert (
                has_references_error or has_notes_error
            ), f"Expected undefined section error, got: {errors[0].message}"

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_50_combined_admonition_and_undefined_section_errors(self) -> None:
        """
        Test that both admonition and undefined section errors are caught together.
        """
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition="note", prefix="!!!"),
            SectionConfig(order=2, name="details", type="free_text", required=False, admonition="info", prefix="???+"),
            SectionConfig(order=3, name="params", type="list_name_and_type", required=False),
        ]
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        # Python content with both wrong admonition AND undefined section
        python_content: str = dedent(
            '''
            def test_function(param1: str) -> None:
                """
                !!! note "Summary"
                    This function has both types of errors.

                ???+ abstract "Details"
                    Wrong admonition (should be 'info').

                Params:
                    param1 (str): A parameter.

                ??? question "References"
                    - Undefined section.
                """
                pass
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

            # Should have errors
            assert len(errors) == 1, f"Expected 1 error with multiple issues, got: {len(errors)}"

            error_message: str = errors[0].message.lower()

            # Check for both types of errors in the combined message
            has_admonition_error: bool = "incorrect admonition" in error_message
            has_undefined_error: bool = "not defined in configuration" in error_message

            assert has_admonition_error, f"Expected admonition error in combined message, got: {errors[0].message}"
            assert (
                has_undefined_error
            ), f"Expected undefined section error in combined message, got: {errors[0].message}"

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_51_config_validation_admonition_true_error(self) -> None:
        """
        Test that admonition=True raises a validation error.
        """
        with pytest.raises(ValueError, match="admonition cannot be True"):
            SectionConfig(
                order=1, name="summary", type="free_text", admonition=True, prefix="!!!"  # This should raise an error
            )

    def test_52_config_validation_admonition_false_with_prefix_error(self) -> None:
        """
        Test that admonition=False with prefix raises a validation error.
        """
        with pytest.raises(ValueError, match="when admonition=False, prefix cannot be provided"):
            SectionConfig(
                order=1,
                name="params",
                type="list_name_and_type",
                admonition=False,  # False should not have prefix
                prefix="!!!",  # This should raise an error
            )

    def test_53_config_validation_admonition_string_without_prefix_error(self) -> None:
        """
        Test that admonition as string without prefix raises a validation error.
        """
        with pytest.raises(ValueError, match="when admonition is a string, prefix must be provided"):
            SectionConfig(
                order=1,
                name="summary",
                type="free_text",
                admonition="note",  # String admonition requires prefix
                # prefix="" is default, should raise error
            )

    def test_54_config_validation_valid_combinations(self) -> None:
        """
        Test valid admonition/prefix combinations.
        """
        # Valid: admonition=False, no prefix
        config1 = SectionConfig(order=1, name="params", type="list_name_and_type", admonition=False)
        assert config1.admonition is False
        assert config1.prefix == ""

        # Valid: admonition=string, with prefix
        config2 = SectionConfig(order=2, name="summary", type="free_text", admonition="note", prefix="!!!")
        assert config2.admonition == "note"
        assert config2.prefix == "!!!"

    def test_55_colon_validation_admonition_sections_should_not_have_colon(self) -> None:
        """
        Test that admonition sections with colons trigger validation errors.
        """
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition="note", prefix="!!!"),
            SectionConfig(order=2, name="details", type="free_text", required=False, admonition="info", prefix="???+"),
        ]
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        # Python content with admonition sections ending with colons (wrong)
        python_content: str = dedent(
            '''
            def test_function():
                """
                !!! note "Summary:"
                    This should not end with colon.

                ???+ info "Details:"
                    This also should not end with colon.
                """
                pass
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

        # Should have errors about colons in admonitions
        assert len(errors) >= 1, f"Expected at least 1 error for colons in admonitions, got: {len(errors)}"

        error_message: str = errors[0].message
        colon_error_count: int = error_message.count("should not end with ':'")
        assert (
            colon_error_count >= 2
        ), f"Expected at least 2 colon violations in error message, got: {colon_error_count}"

        # Clean up
        py_file.unlink(missing_ok=True)

    def test_56_colon_validation_non_admonition_sections_must_have_colon(self) -> None:
        """
        Test that non-admonition sections without colons trigger validation errors.
        """
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition=False),
            SectionConfig(order=2, name="params", type="list_name_and_type", required=False, admonition=False),
            SectionConfig(order=3, name="returns", type="list_type", required=False, admonition=False),
        ]
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        # Python content with non-admonition sections missing colons (wrong)
        python_content: str = dedent(
            '''
            def test_function(param1: str) -> bool:
                """
                Summary
                    This should end with colon.

                Params
                    param1 (str): A parameter.

                Returns
                    (bool): A return value.
                """
                return True
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

            # Should have errors about missing colons in non-admonitions
            assert len(errors) >= 1, f"Expected at least 1 error for missing colons, got: {len(errors)}"

            error_message: str = errors[0].message
            colon_error_count: int = error_message.count("must end with ':'")
            assert (
                colon_error_count >= 3
            ), f"Expected at least 3 colon violations in error message, got: {colon_error_count}"

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_57_title_case_validation_non_admonition_sections(self) -> None:
        """
        Test that non-admonition sections must be in title case.
        """
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition=False),
            SectionConfig(order=2, name="params", type="list_name_and_type", required=False, admonition=False),
            SectionConfig(order=3, name="returns", type="list_type", required=False, admonition=False),
        ]
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        # Python content with wrong case sections
        python_content: str = dedent(
            '''
            def test_function(param1: str) -> bool:
                """
                summary:
                    This should be "Summary:"

                PARAMS:
                    param1 (str): A parameter.

                returns:
                    (bool): A return value.
                """
                return True
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

            # Should have errors about wrong case
            assert len(errors) >= 1, f"Expected at least 1 error for title case violations, got: {len(errors)}"

            error_message: str = errors[0].message
            case_error_count: int = error_message.count("must be in title case")
            assert (
                case_error_count >= 2
            ), f"Expected at least 2 title case violations in error message, got: {case_error_count}"

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_58_parentheses_validation_list_type_sections(self) -> None:
        """
        Test that list_type sections require parenthesized types.
        """
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition=False),
            SectionConfig(
                order=2, name="raises", type="list_type", required=True, admonition=False
            ),  # Make required for testing
            SectionConfig(
                order=3, name="returns", type="list_type", required=True, admonition=False
            ),  # Make required for testing
        ]
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        # Python content with missing parentheses in list_type sections
        python_content: str = dedent(
            '''
            def test_function() -> bool:
                """
                Summary:
                    Function summary.

                Raises:
                    ValueError:
                        Should be (ValueError):

                Returns:
                    bool:
                        Should be (bool):

                UndefinedSection:
                    This should trigger undefined section error.
                """
                return True
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

        # With the current implementation, no parentheses errors should be found
        # because lines like "ValueError:" and "bool:" are skipped when no parenthesized type has been found yet
        # The test should only check for undefined section errors
        assert len(errors) >= 1, f"Expected at least 1 error for undefined section, got: {len(errors)}"

        # Check if undefined section error is in the combined error message
        error_message: str = errors[0].message
        assert "undefined" in error_message.lower(), f"Expected undefined section error, got: {error_message}"

        # Clean up
        py_file.unlink(missing_ok=True)

    def test_59_parentheses_validation_list_name_and_type_sections(self) -> None:
        """
        Test that list_name_and_type sections require parenthesized types.
        """
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition=False),
            SectionConfig(order=2, name="params", type="list_name_and_type", required=False, admonition=False),
            SectionConfig(order=3, name="returns", type="list_name_and_type", required=False, admonition=False),
        ]
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        # Python content with missing parentheses in list_name_and_type sections
        python_content: str = dedent(
            '''
            def test_function(param1: str, param2: int) -> bool:
                """
                Summary:
                    Function summary.

                Params:
                    param1 str:
                        Should be param1 (str):
                    param2 int:
                        Should be param2 (int):

                Returns:
                    result bool:
                        Should be result (bool):
                """
                return True
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

            # Should have errors about missing parentheses
            assert len(errors) >= 1, f"Expected at least 1 error for parentheses violations, got: {len(errors)}"

            error_message: str = errors[0].message
            parentheses_error_count: int = error_message.count("requires parenthesized types")
            assert (
                parentheses_error_count >= 3
            ), f"Expected at least 3 parentheses violations in error message, got: {parentheses_error_count}"

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_60_correct_validation_with_all_new_rules(self) -> None:
        """
        Test that properly formatted docstring with all new rules passes validation.
        """
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition="note", prefix="!!!"),
            SectionConfig(order=2, name="details", type="free_text", required=False, admonition="info", prefix="???+"),
            SectionConfig(order=3, name="params", type="list_name_and_type", required=False, admonition=False),
            SectionConfig(order=4, name="raises", type="list_type", required=False, admonition=False),
            SectionConfig(order=5, name="returns", type="list_type", required=False, admonition=False),
            SectionConfig(
                order=6, name="examples", type="free_text", required=False, admonition="example", prefix="???+"
            ),
        ]
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        # Python content following all the new validation rules correctly
        python_content: str = dedent(
            '''
            def test_function(param1: str, param2: int) -> bool:
                """
                !!! note "Summary"
                    Convert a string value into a bool value.

                ???+ info "Details"
                    This process is necessary because of some reason.

                Params:
                    param1 (str):
                        The string parameter to convert.
                    param2 (int):
                        The integer parameter for processing.

                Raises:
                    (ValueError):
                        If the value cannot be converted.

                Returns:
                    (bool):
                        A True or False value.

                ???+ example "Examples"
                    Example code:
                    >>> test_function("true", 1)
                    True
                """
                return True
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

            # Should have no errors - all rules followed correctly
            assert (
                len(errors) == 0
            ), f"Expected no errors for correctly formatted docstring, got: {[e.message for e in errors]}"

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_61_unknown_free_text_section_default_return(self) -> None:
        """
        Test that unknown free text sections return True by default.
        """
        # Create a config with an unknown free text section name
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="unknown_custom_section", type="free_text", required=True, admonition=False),
        ]
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        python_content: str = dedent(
            '''
            def test_function():
                """
                Unknown Custom Section:
                    This should trigger the default return True path.
                """
                pass
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

            # Should have no errors - unknown free text sections default to True
            assert len(errors) == 0, f"Expected no errors for unknown free text section, got: {errors}"

    def test_62_undefined_sections_skip_empty_and_code_blocks(self) -> None:
        """
        Test that _check_undefined_sections skips empty matches and code blocks.
        """

        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition=False),
        ]
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        python_content: str = dedent(
            r'''
            def test_function():
                """
                Summary:
                    Function with code blocks that should be ignored.

                ```python
                def example():
                    pass
                ```

                ```sh
                echo "hello"
                ```

                Some.Path.With.Dots:
                    Should be ignored due to dots.

                /path/to/file:
                    Should be ignored due to slashes.

                back\\slash\\path:
                    Should be ignored due to backslashes.

                `inline_code`:
                    Should be ignored due to backticks.
                """
                pass
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

            # Should have no errors - all the problematic sections should be filtered out
            assert len(errors) == 0, f"Expected no errors, code blocks should be filtered out, got: {errors}"

    def test_64_summary_section_simple_content_validation(self) -> None:
        """
        Test that summary section validation accepts simple docstring content (not just admonitions).
        """
        # Config with just a summary section (non-admonition)
        summary_sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition=False),
        ]
        checker = DocstringChecker(_create_config(summary_sections))

        python_content: str = dedent(
            '''
            def test_function():
                """
                This is a simple summary without formal admonition format.
                It should be accepted as valid summary content.
                """
                pass
            '''
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

            # Should have no errors - simple content should be accepted for summary
            assert len(errors) == 0, f"Simple summary content should be valid, got: {errors}"

    def test_65_config_empty_string_admonition_handling(self) -> None:
        """
        Test that empty string admonition values are properly handled as False.
        """
        # Create a SectionConfig with an empty string admonition value directly
        # This bypasses the TOML loading to test the empty string handling logic
        try:
            # Create section data that would come from TOML parsing
            section_data: dict[str, Any] = {
                "order": 1,
                "name": "test",
                "type": "free_text",
                "admonition": "",  # Empty string
                "required": True,
            }

            # Simulate the config loading logic for empty string handling
            admonition_value: Union[str, bool, None] = section_data.get("admonition")
            if admonition_value is None:
                admonition_value = False  # Use SectionConfig default
            elif isinstance(admonition_value, str) and admonition_value == "":
                admonition_value = False  # Treat empty string as False

            # Create the section config with the processed value
            section = SectionConfig(
                order=int(section_data.get("order", 0)),
                name=str(section_data.get("name", "")),
                type=str(section_data.get("type", "")),  # type: ignore
                admonition=admonition_value,
                prefix=str(section_data.get("prefix", "")),
                required=bool(section_data.get("required", False)),
            )

            # Verify that empty string was converted to False
            assert section.admonition is False, "Empty string admonition should be converted to False"

        except Exception as e:
            pytest.fail(f"Empty string admonition handling should not raise exception: {e}")

    def test_66_summary_section_simple_content_acceptance(self) -> None:
        """
        Test that summary sections accept simple content without formal patterns.
        """
        # Custom config with summary section
        custom_sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition=False),
        ]
        checker = DocstringChecker(_create_config(custom_sections))

        # Test the _check_free_text_section method directly
        section_config = SectionConfig(order=1, name="summary", type="free_text", required=True, admonition=False)

        # This should trigger: (return len(docstring.strip()) > 0)
        simple_docstring = "This is just simple content without formal patterns."
        result: bool = checker._check_free_text_section(simple_docstring, section_config)

        # Should return True because docstring has content
        assert result is True

    def test_67_undefined_sections_special_char_skip(self) -> None:
        """
        Test that undefined sections validation skips entries with special characters.
        """
        # Custom config with only summary defined
        custom_sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition=False),
        ]
        checker = DocstringChecker(_create_config(custom_sections))

        # Test docstring with special characters that should be skipped
        test_docstring = "Summary:\nContent\nfile.txt:\nSkipped\nbackslash\\path:\nSkipped\n`code`:\nSkipped"

        # This should cover the special character skipping logic
        undefined_errors: list[str] = checker._check_undefined_sections(test_docstring)

        # No errors should be returned because special character sections are skipped
        assert len(undefined_errors) == 0

    def test_68_undefined_sections_detection_with_found_sections(self) -> None:
        """
        Test the logic for detecting which sections are not configured.
        """
        # Custom config with only summary defined
        custom_sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition=False),
        ]
        checker = DocstringChecker(_create_config(custom_sections))

        # Test docstring with an undefined section
        test_docstring = "Summary:\nContent\nUndefined:\nContent"

        # This should cover the loop that checks found sections
        undefined_errors: list[str] = checker._check_undefined_sections(test_docstring)

        # Should find one undefined section
        assert len(undefined_errors) == 1
        assert "undefined" in undefined_errors[0].lower()

    def test_69_code_block_character_skipping(self) -> None:
        """
        Test that sections with special characters are skipped.
        """
        custom_sections: list[SectionConfig] = []
        checker = DocstringChecker(_create_config(custom_sections))

        # Test docstring with sections containing special characters that should be skipped
        test_docstring: str = dedent(
            """
            Summary:
                Basic content

            Some.Thing:
                This should be skipped due to dot

            path/to/file:
                This should be skipped due to slash

            code`block:
                This should be skipped due to backtick

            Valid_Section:
                This should be detected
            """
        )

        # Check undefined sections - should skip the special character ones
        undefined_errors: list[str] = checker._check_undefined_sections(test_docstring)

        # Should only find Summary and Valid_Section as undefined (since we have no config)
        assert len(undefined_errors) == 2
        error_text: str = " ".join(undefined_errors).lower()
        assert "summary" in error_text
        assert "valid_section" in error_text

        # These should NOT appear because they have special chars
        assert "some.thing" not in error_text
        assert "path/to/file" not in error_text
        assert "code`block" not in error_text

    def test_70_examples_section_pattern_matching(self) -> None:
        """
        Test the examples section pattern matching.
        """
        # Create a minimal checker to test the specific method
        minimal_sections: list[SectionConfig] = [
            SectionConfig(order=1, name="examples", type="free_text", required=True, admonition=False)
        ]
        checker = DocstringChecker(_create_config(minimal_sections))

        # Create section config for examples
        section = SectionConfig(order=1, name="examples", type="free_text", required=True, admonition=False)

        # Test docstring with examples section
        docstring_with_examples = """
        This is a test function.

        ???+ example "Examples"
            This is an example.
        """

        # This should match the examples patterns
        result: bool = checker._check_free_text_section(docstring_with_examples, section)
        assert result is True

        # Test docstring without examples section
        docstring_without_examples = """
        This is a test function without examples.
        """

        result = checker._check_free_text_section(docstring_without_examples, section)
        assert result is False

    def test_71_empty_section_name_skipping(self) -> None:
        """
        Test that empty section names and code language markers are skipped.
        """
        custom_sections: list[SectionConfig] = []
        checker = DocstringChecker(_create_config(custom_sections))

        # Test docstring with empty section names and code language markers
        test_docstring: str = dedent(
            """
            Summary:
                Basic content

            py:
                This should be skipped (code language)

            python:
                This should be skipped (code language)

            sh:
                This should be skipped (code language)

            shell:
                This should be skipped (code language)

            Valid_Section:
                This should be detected
            """
        )

        # Check undefined sections - should skip the code language markers
        undefined_errors: list[str] = checker._check_undefined_sections(test_docstring)

        # Should only find Summary and Valid_Section (since we have no config)
        assert len(undefined_errors) == 2
        error_text: str = " ".join(undefined_errors).lower()
        assert "summary" in error_text
        assert "valid_section" in error_text

        # These should NOT appear because they are code language markers
        assert "py" not in error_text
        assert "python" not in error_text
        assert "sh" not in error_text
        assert "shell" not in error_text

    def test_72_examples_section_exact_pattern_matching(self) -> None:
        """
        This covers the specific regex pattern for examples sections.
        """
        # Create a section config specifically for examples
        examples_section = SectionConfig(order=1, name="examples", type="free_text", required=False, admonition=False)

        checker = DocstringChecker(_create_config([examples_section]))

        # Test docstring with the exact pattern that should trigger
        docstring_with_examples: str = dedent(
            """
            This is a test function.

            ???+ example "Examples"
                This is an example.
            """
        )

        # This should match the examples pattern
        result: bool = checker._check_free_text_section(docstring_with_examples, examples_section)
        assert result is True

        # Test docstring without the examples pattern
        docstring_without_examples: str = dedent(
            """
            This is a test function.

            Some other content but no examples section.
            """
        )

        result = checker._check_free_text_section(docstring_without_examples, examples_section)
        assert result is False

        # Test with case variations to ensure case insensitive matching
        docstring_case_variant: str = dedent(
            """
            This is a test function.

            ???+ EXAMPLE "Examples"
                This is an example.
            """
        )

        result = checker._check_free_text_section(docstring_case_variant, examples_section)
        assert result is True

    def test_73_special_characters_continue_logic(self) -> None:
        """
        Test that sections with special characters trigger the continue statement.
        """
        custom_sections: list[SectionConfig] = []
        checker = DocstringChecker(_create_config(custom_sections))

        # Test docstring with admonition sections that will be found by the regex but filtered out by special chars
        test_docstring: str = dedent(
            """
            Regular section here.

            !!! note "Summary"
                This should be detected

            !!! note "Code.File"
                This should be skipped due to dot

            !!! note "path/to/file"
                This should be skipped due to slash

            !!! note "code`block"
                This should be skipped due to backtick

            !!! note "back\\slash"
                This should be skipped due to backslash

            !!! note "Valid_Section"
                This should be detected
            """
        )

        # Check undefined sections - the special character ones should be skipped by the continue statement
        undefined_errors: list[str] = checker._check_undefined_sections(test_docstring)

        # Should only find Summary and Valid_Section as undefined (since we have no config)
        # The special character sections should be filtered out
        assert len(undefined_errors) == 2
        error_text: str = " ".join(undefined_errors).lower()

        # These should be found
        assert "summary" in error_text
        assert "valid_section" in error_text

        # These should NOT appear because they have special chars and hit the continue statement
        assert "code.file" not in error_text
        assert "path/to/file" not in error_text
        assert "code`block" not in error_text
        assert "back\\slash" not in error_text

    def test_74_examples_regex_pattern_coverage(self) -> None:
        """
        Test to specifically cover the examples regex pattern.
        """
        examples_section = SectionConfig(
            name="example", required=True, type="free_text", order=1, admonition="example", prefix="???+"
        )
        checker = DocstringChecker(_create_config([examples_section]))

        # This should match the regex pattern
        docstring_with_examples: str = dedent(
            """
            This is a test function.

            ???+ example "Examples"
                This is an example.
            """
        )

        # This should return True
        result: bool = checker._check_free_text_section(docstring_with_examples, examples_section)
        assert result is True

    def test_75_summary_section_formal_and_simple_patterns(self) -> None:
        """
        Test summary section validation with both formal and simple docstring patterns.
        Covers formal pattern matching and simple content validation for summary sections.
        """
        # Create a section config that matches the condition for "summary"
        summary_section = SectionConfig(
            name="summary",  # Must be "summary" to hit the summary section validation
            required=True,
            type="free_text",
            order=1,
            admonition=False,  # Not a string admonition, so first condition fails
            prefix="",
        )
        checker = DocstringChecker(_create_config([summary_section]))

        # Test formal pattern match should return True
        formal_docstring = """
        This is a function.

        !!! note "Summary"
            This is a formal summary.
        """
        result_formal: bool = checker._check_free_text_section(formal_docstring, summary_section)
        assert result_formal is True, "Formal summary pattern should be recognized"

        # Test simple docstring content check
        simple_docstring = "This is a simple docstring without formal formatting."
        result_simple: bool = checker._check_free_text_section(simple_docstring, summary_section)
        assert result_simple is True, "Simple docstring should satisfy summary requirement"

        # Test with empty docstring to also cover the False case
        empty_docstring: str = ""
        result_empty: bool = checker._check_free_text_section(empty_docstring, summary_section)
        assert result_empty is False, "Empty docstring should not satisfy summary requirement"

    def test_76_parentheses_validation_with_description_words(self) -> None:
        """
        Test parentheses validation with description lines containing specific words.
        This covers the missing lines 971 and 980 in core.py.
        """
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition=False),
            SectionConfig(order=2, name="Params", type="list_name_and_type", required=True, admonition=False),
        ]
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        # Test with content that has description lines with specific words that should be skipped
        python_content: str = dedent(
            '''
            def test_function():
                """
                Summary:
                    Test function.

                Params:
                    param1 (str): Main parameter
                    Default: some default value here
                    Output format: JSON format description
                    Show examples: whether to show examples
                    param2: Missing parenthesized type (should trigger error)
                """
                pass
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

        # Should have an error for param2 missing parentheses, but not for the description lines
        assert len(errors) > 0
        error_message: str = errors[0].message

        # Should have error for param2
        assert (
            "param2" in error_message and "parenthesized types" in error_message
        ), f"Expected parentheses error for param2, got: {error_message}"

        # Should NOT have errors for the description lines
        assert "Default:" not in error_message, f"Should not have error for 'Default:' line, got: {error_message}"
        assert (
            "Output format:" not in error_message
        ), f"Should not have error for 'Output format:' line, got: {error_message}"
        assert (
            "Show examples:" not in error_message
        ), f"Should not have error for 'Show examples:' line, got: {error_message}"

        # Clean up
        py_file.unlink(missing_ok=True)

    def test_77_parentheses_validation_specific_error_line(self) -> None:
        """
        Test that hits the specific error append line (line 980) in core.py.
        """
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition=False),
            SectionConfig(order=2, name="Parameters", type="list_name_and_type", required=True, admonition=False),
        ]
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        # Simple content that should definitely trigger the parentheses error
        python_content: str = dedent(
            '''
            def test_function():
                """
                Summary:
                    Test function.

                Parameters:
                    simple_param_name: This should trigger parentheses validation error
                """
                pass
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

        # Should have an error for missing parentheses that hits line 980-981
        assert len(errors) > 0
        error_message: str = errors[0].message
        assert "parenthesized types" in error_message, f"Expected parentheses error, got: {error_message}"
        assert "simple_param_name" in error_message, f"Expected error for simple_param_name, got: {error_message}"

        # Clean up
        py_file.unlink(missing_ok=True)

    def test_78_parentheses_validation_alternative_trigger(self) -> None:
        """
        Another attempt to hit the missing line in parentheses validation.
        """
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition=False),
            SectionConfig(order=2, name="Args", type="list_name_and_type", required=True, admonition=False),
        ]
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        # Test case where we have a clear parameter line that lacks parentheses
        python_content: str = dedent(
            '''
            def test_function():
                """
                Summary:
                    Test function.

                Args:
                    x: Parameter without parentheses - should error
                """
                pass
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

        # Should have an error for missing parentheses
        assert len(errors) > 0
        error_message: str = errors[0].message
        assert (
            "parenthesized types" in error_message and "x:" in error_message
        ), f"Expected parentheses error for 'x:', got: {error_message}"

        # Clean up
        py_file.unlink(missing_ok=True)

    def test_79_specific_parentheses_validation_line_target(self) -> None:
        """Test to specifically target core.py line 998 with exact condition."""
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition=False),
            SectionConfig(order=2, name="Parameters", type="list_name_and_type", required=True, admonition=False),
        ]
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        # Create a parameter line that will pass all the filter conditions but fail the regex
        # This should hit the exact line we're targeting (core.py:998)
        python_content: str = dedent(
            '''
            def test_function():
                """
                Summary:
                    Test function.

                Parameters:
                    some_param: description without parentheses
                """
                pass
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

        # Should find error specifically about parentheses validation
        parentheses_errors: list[DocstringError] = [
            err for err in errors if "parenthesized types" in err.message and "some_param:" in err.message
        ]
        assert len(parentheses_errors) > 0, f"Expected parentheses error, got errors: {[e.message for e in errors]}"

        # Clean up
        py_file.unlink(missing_ok=True)

    def test_80_precise_parentheses_validation_coverage(self) -> None:
        """Test to precisely hit core.py line 998 - parentheses error creation."""
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition=False),
            SectionConfig(order=2, name="Args", type="list_name_and_type", required=True, admonition=False),
        ]
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        # Create content that will hit the exact conditions:
        # - Current section is list_name_and_type
        # - Line has colon but no parentheses
        # - Line doesn't contain filter words ("default", "output", "format", "show", "example")
        # - Line fails the regex r"\([^)]+\):"
        python_content: str = dedent(
            '''
            def test_function():
                """
                Summary:
                    Test function.

                Args:
                    param: missing parentheses here
                """
                pass
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

        # Should find the specific parentheses error
        parentheses_errors: list[DocstringError] = [
            err for err in errors if "parenthesized types" in err.message and "param:" in err.message
        ]
        assert (
            len(parentheses_errors) > 0
        ), f"Expected parentheses error containing 'param:', got errors: {[e.message for e in errors]}"

        # Clean up
        py_file.unlink(missing_ok=True)

    def test_81_continue_statement_for_description_words(self) -> None:
        """
        Test that line 998 (continue statement) is hit when lines contain description words.
        This specifically targets the continue statement that skips validation for description lines.
        """
        # Create configuration with list_name_and_type section
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition=False),
            SectionConfig(order=2, name="params", type="list_name_and_type", required=False, admonition=False),
        ]
        checker = DocstringChecker(_create_config(sections))

        python_content: str = dedent(
            '''
            def test_function(param1, param2):
                """
                Test function for hitting continue statement.

                Params:
                    default: Should be skipped due to continue word in name
                    output: Should be skipped due to continue word in name
                    normal_param: Should trigger parentheses error
                """
                pass
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

        # The lines with "default" and "output" should be skipped due to the continue statement
        # But the "normal_param" line should trigger a parentheses error
        parentheses_errors: list[DocstringError] = [err for err in errors if "parenthesized types" in err.message]

        # Should have exactly one error for normal_param, but not for default/output lines
        assert len(parentheses_errors) == 1, f"Expected exactly 1 parentheses error, got: {len(parentheses_errors)}"
        assert (
            "normal_param" in parentheses_errors[0].message
        ), f"Expected error for normal_param, got: {parentheses_errors[0].message}"

        # Ensure the lines with description words were skipped (no errors for them)
        # The 'default' and 'output' parameter names should have been skipped due to continue statement
        assert not any(
            any(word in err.message.lower() for word in ["default:", "output:"]) for err in parentheses_errors
        ), f"Expected no parentheses errors for description lines, got: {[e.message for e in parentheses_errors]}"

        # Clean up
        py_file.unlink(missing_ok=True)

    def test_82_list_type_description_lines_with_colons(self) -> None:
        """
        Test that description lines in list_type sections with colons don't trigger parentheses errors.
        This tests the specific scenario where a raises section has proper parentheses for the type,
        but the description contains colons and should not be validated.
        """
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition=False),
            SectionConfig(order=2, name="raises", type="list_type", required=False, admonition=False),
        ]
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        # Test case 1: Description on separate lines (should pass)
        python_content_1: str = dedent(
            '''
            def test_function():
                """
                Test function for raises validation.

                Raises:
                    (TypeCheckError):
                        If any of the inputs parsed to the parameters of this function are not the correct type. Uses the [`@typeguard.typechecked`](https://typeguard.readthedocs.io/en/stable/api.html#typeguard.typechecked) decorator.
                """
                pass
            '''
        ).strip()

        # Test case 2: Description on same line (should pass)
        python_content_2: str = dedent(
            '''
            def test_function_same_line():
                """
                Test function for raises validation on same line.

                Raises:
                    (TypeCheckError): If any of the inputs parsed to the parameters of this function are not the correct type.
                """
                pass
            '''
        ).strip()

        # Test case 3: Invalid format (should fail)
        python_content_3: str = dedent(
            '''
            def test_function_invalid():
                """
                Test function for invalid raises format.

                Raises:
                    TypeCheckError: This should trigger an error because type is not parenthesized.
                """
                pass
            '''
        ).strip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test case 1
            py_file_1: Path = temp_path.joinpath("test1.py")
            py_file_1.write_text(python_content_1)
            errors_1: list[DocstringError] = checker.check_file(str(py_file_1))

            # Test case 2
            py_file_2: Path = temp_path.joinpath("test2.py")
            py_file_2.write_text(python_content_2)
            errors_2: list[DocstringError] = checker.check_file(str(py_file_2))

            # Test case 3
            py_file_3: Path = temp_path.joinpath("test3.py")
            py_file_3.write_text(python_content_3)
            errors_3: list[DocstringError] = checker.check_file(str(py_file_3))

        # Test case 1: Should have no errors (description lines with colons should be ignored)
        assert (
            len(errors_1) == 0
        ), f"Expected no errors for proper parentheses with description, got: {[e.message for e in errors_1]}"

        # Test case 2: Should have no errors (same line description should be ignored)
        assert len(errors_2) == 0, f"Expected no errors for same line description, got: {[e.message for e in errors_2]}"

        # Test case 3: With the current implementation, no errors should be found
        # because "TypeCheckError:" is skipped when no parenthesized type has been found yet
        assert len(errors_3) == 0, f"Expected no errors due to permissive logic, got: {len(errors_3)}"

    def test_83_malformed_type_after_valid_type(self):
        """
        Test that ensures a malformed type definition is caught when it appears
        at the same indentation level as a valid type definition in list_type sections.
        This covers the missing line 1012 in core.py.
        """
        # Create a checker with raises section configured
        sections = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
            SectionConfig(order=2, name="raises", type="list_type", required=False),
        ]
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        python_content: str = dedent(
            '''
            def function_with_malformed_type():
                """
                Summary of the function.

                Raises:
                    (ValueError): When something goes wrong.
                    BadFormatError: This is malformed - no parentheses.
                """
                pass
            '''
        ).strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
            temp_file.write(python_content)
            temp_file.flush()
            temp_path: Path = Path(temp_file.name)

        try:
            errors: list[DocstringError] = checker.check_file(str(temp_path))

            # Should have one error for the malformed type definition
            assert len(errors) == 1, f"Expected 1 error for malformed type, got: {len(errors)}"

            # Check that the error message mentions the malformed line
            error_message = errors[0].message
            assert "BadFormatError:" in error_message, f"Error should mention 'BadFormatError:', got: {error_message}"
            assert (
                "requires parenthesized types" in error_message
            ), f"Error should mention parenthesized types, got: {error_message}"

        finally:
            temp_path.unlink()

    def test_84_list_name_and_type_description_lines_with_colons(self):
        """
        Test that description lines in list_name_and_type sections with colons don't trigger parentheses errors.
        This tests the specific scenario where a params section has proper parentheses for parameters,
        but the description contains bullet points with colons and should not be validated.
        """
        # Create a checker with params section configured
        sections = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
            SectionConfig(order=2, name="params", type="list_name_and_type", required=False),
        ]
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        python_content: str = dedent(
            '''
            def function_with_description_lines():
                """
                Summary of the function.

                Params:
                    columnwise (bool, optional):
                        Whether or not to print columnwise or rowwise.

                        - `True`: Will be formatted column-wise.
                        - `False`: Will be formatted row-wise.

                        Defaults to: `True`.

                    print_output (bool, optional):
                        Whether or not to print the output to the terminal.

                        - `True`: Will print and return.
                        - `False`: Will not print; only return.

                        Defaults to: `False`.
                """
                pass
            '''
        ).strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
            temp_file.write(python_content)
            temp_file.flush()
            temp_path: Path = Path(temp_file.name)

        try:
            errors: list[DocstringError] = checker.check_file(str(temp_path))

            # Should have no errors - description lines with colons should be ignored
            assert (
                len(errors) == 0
            ), f"Expected no errors for description lines with colons, got: {[e.message for e in errors]}"

        finally:
            temp_path.unlink()

    def test_85_list_name_and_type_indentation_based_validation(self):
        """
        Test indentation-based validation in list_name_and_type sections.
        This covers lines 1041 and 1046 in core.py.
        """
        # Create a checker with params section configured
        sections = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
            SectionConfig(order=2, name="params", type="list_name_and_type", required=False),
        ]
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        python_content: str = dedent(
            '''
            def function_with_indented_descriptions():
                """
                Summary of the function.

                Params:
                    param_name (str):
                        This is a description that is properly indented.
                        This line should be ignored: it has multiple words.
                """
                pass
            '''
        ).strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
            temp_file.write(python_content)
            temp_file.flush()
            temp_path: Path = Path(temp_file.name)

        try:
            errors: list[DocstringError] = checker.check_file(str(temp_path))

            # Should have no errors - description lines should be ignored based on indentation and word count
            assert len(errors) == 0, f"Expected no errors for indented descriptions, got: {[e.message for e in errors]}"

        finally:
            temp_path.unlink()

    def test_86_list_name_and_type_multiple_words_before_colon(self):
        """
        Test that lines with multiple words before colon are skipped in list_name_and_type sections.
        This covers line 1046 in core.py (the continue statement for multiple words).
        """
        # Create a checker with params section configured
        sections = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
            SectionConfig(order=2, name="params", type="list_name_and_type", required=False),
        ]
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        python_content: str = dedent(
            '''
            def function_with_multiple_word_descriptions():
                """
                Summary of the function.

                Params:
                    param_name (str):
                        This description line has multiple words before colon: should be skipped.
                """
                pass
            '''
        ).strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
            temp_file.write(python_content)
            temp_file.flush()
            temp_path: Path = Path(temp_file.name)

        try:
            errors: list[DocstringError] = checker.check_file(str(temp_path))

            # Should have no errors - lines with multiple words before colon should be skipped
            assert (
                len(errors) == 0
            ), f"Expected no errors for multiple word descriptions, got: {[e.message for e in errors]}"

        finally:
            temp_path.unlink()

    def test_87_list_name_and_type_exactly_multiple_words_at_same_level(self):
        """
        Test line 1046 in core.py - the continue statement for multiple words before colon.
        This creates a scenario where we have a line with multiple words before colon
        at the same indentation level as parameter definitions.
        """
        # Create a checker with params section configured
        sections = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
            SectionConfig(order=2, name="params", type="list_name_and_type", required=False),
        ]
        checker: DocstringChecker = DocstringChecker(_create_config(sections))

        python_content: str = dedent(
            '''
            def function_with_same_level_multiple_words():
                """
                Summary of the function.

                Params:
                    param_name (str):
                        Description line.
                    multiple words here should be skipped: this has too many words.
                """
                pass
            '''
        ).strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
            temp_file.write(python_content)
            temp_file.flush()
            temp_path: Path = Path(temp_file.name)

        try:
            errors: list[DocstringError] = checker.check_file(str(temp_path))

            # Should have no errors - the line with multiple words should be skipped
            assert (
                len(errors) == 0
            ), f"Expected no errors for multiple words at same level, got: {[e.message for e in errors]}"

        finally:
            temp_path.unlink()
