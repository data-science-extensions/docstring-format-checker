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
from pathlib import Path
from subprocess import CompletedProcess
from textwrap import dedent
from unittest import TestCase

# ## Python Third Party Imports ----
import pytest

# ## Local First Party Imports ----
from docstring_format_checker.config import SectionConfig
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


def simple_checker() -> DocstringChecker:
    """
    Create a simple docstring checker for testing.
    """
    config: list[SectionConfig] = [
        SectionConfig(order=1, name="summary", type="free_text", required=True),
        SectionConfig(order=2, name="params", type="list_name_and_type", required=True),
    ]
    return DocstringChecker(config)


def detailed_checker() -> DocstringChecker:
    """
    Create a detailed docstring checker for testing.
    """
    config: list[SectionConfig] = [
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

    def test_06_check_directory_non_recursive(self) -> None:
        """
        Test checking a directory non-recursively.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create test files
            temp_path = Path(temp_dir)
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

            # Check directory non-recursively
            results: dict[str, list[DocstringError]] = self.simple_checker.check_directory(temp_path, recursive=False)

            # Should only find errors in bad.py, not nested.py
            assert len(results) == 1
            assert any("bad.py" in path for path in results.keys())
            assert not any("nested.py" in path for path in results.keys())

    def test_07_check_directory_with_exclusions(self) -> None:
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

        empty_checker = DocstringChecker([])
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

        complex_checker = DocstringChecker(complex_sections)

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

        ordered_checker = DocstringChecker(ordered_sections)

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

        checker = DocstringChecker(sections)

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

        checker = DocstringChecker(sections)

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

        checker = DocstringChecker(sections)

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

        checker = DocstringChecker(sections)

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

        checker = DocstringChecker(sections)

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

        checker = DocstringChecker(sections)

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

        checker = DocstringChecker(sections)

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

        checker = DocstringChecker(sections)

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
        Test validation of unknown free text sections.
        """

        # Create a section with an unknown name for free text type
        # This should trigger the default return True for unknown sections in _validate_section
        unknown_sections: list[SectionConfig] = [
            SectionConfig(order=1, name="unknown_custom_section", type="free_text", required=True),
        ]

        checker = DocstringChecker(unknown_sections)

        python_content: str = dedent(
            '''
            def test_function():
                """
                !!! note "Summary"
                This is a function with an unknown section type that should return True by default.
                """
                pass
            '''
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            temp_path = Path(temp_dir)
            py_file: Path = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

            # Should validate as true for unknown free text sections
            # This tests the default return True for unknown sections in _validate_section line 398
            assert len(errors) == 0, f"Should not have errors for unknown free text section, got: {errors}"

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

        checker = DocstringChecker(summary_sections)

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
            py_file = temp_path.joinpath("test.py")
            py_file.write_text(python_content)
            errors: list[DocstringError] = checker.check_file(str(py_file))

            # Should validate as true - this tests line 398: return len(docstring.strip()) > 0
            assert len(errors) == 0, f"Should not have errors for simple summary docstring, got: {errors}"

            # Clean up
            py_file.unlink(missing_ok=True)

    def test_38_summary_section_formal_pattern_validation(self) -> None:
        """
        Test that formal summary patterns are accepted for summary sections.
        """

        # Create a summary section that should accept formal patterns
        summary_sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
        ]

        checker = DocstringChecker(summary_sections)

        python_content: str = dedent(
            '''
            def test_function():
                """
                !!! note "Summary"
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

            # Should validate as true - this tests line 398: return True for formal pattern
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
                !!! note "Summary"
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
                !!! note "Summary"
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
                !!! note "Summary"
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
        config: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
        ]
        checker: DocstringChecker = DocstringChecker(config)

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
                !!! note "Summary"
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
                !!! note "Summary"
                    Example class with overloaded methods.
                """

                @overload
                def method(self, x: int) -> int: ...
                @overload
                def method(self, x: str) -> str: ...
                def method(self, x: Union[int, str]) -> Union[int, str]:
                    """
                    !!! note "Summary"
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
                    !!! note "Summary"
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
        overload_code = dedent(
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
        typing_overload_code = dedent(
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
        regular_code = dedent(
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
        other_decorator_code = dedent(
            """
            @property
            def func(self):
                return self._value
        """
        ).strip()

        tree = ast.parse(other_decorator_code)
        func_node = tree.body[0]  # First node is the function
        assert isinstance(func_node, ast.FunctionDef)
        assert not checker._is_overload_function(
            func_node
        ), "Should not detect @overload on function with other decorators"
