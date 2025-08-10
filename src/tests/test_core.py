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
import pytest

# ## Local First Party Imports ----
from docstring_format_checker.config import SectionConfig
from docstring_format_checker.core import DocstringChecker
from docstring_format_checker.utils.exceptions import DocstringError


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

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:

            f.write(python_content)
            f.flush()

            errors: list[DocstringError] = self.simple_checker.check_file(f.name)
            assert len(errors) == 0

            Path(f.name).unlink()

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

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:

            f.write(python_content)
            f.flush()

            errors: list[DocstringError] = self.simple_checker.check_file(f.name)
            assert len(errors) == 2  # function and method missing docstrings

            # Check error details
            function_error: DocstringError = next(e for e in errors if e.item_name == "bad_function")
            assert function_error.item_type == "function"
            assert "Missing docstring" in function_error.message

            method_error: DocstringError = next(e for e in errors if e.item_name == "bad_method")
            assert method_error.item_type == "method"

            Path(f.name).unlink()

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
                    param1 (str): First parameter.
                    param2 (int): Second parameter.

                Returns:
                    bool: Return value.

                ???+ example "Examples"
                    Example usage here.
                """
                return True
            '''
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:

            f.write(python_content)
            f.flush()

            errors: list[DocstringError] = self.detailed_checker.check_file(f.name)
            assert len(errors) == 0

            Path(f.name).unlink()

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

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:

            f.write(python_content)
            f.flush()

            errors: list[DocstringError] = self.detailed_checker.check_file(f.name)
            assert len(errors) == 1
            assert "Params" in errors[0].message

            Path(f.name).unlink()

    def test_05_check_directory(self) -> None:
        """
        Test checking a directory of Python files.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            temp_path = Path(temp_dir)

            # Create test files
            (temp_path / "good.py").write_text(
                dedent(
                    '''
                    def good_function():
                        """Good docstring."""
                        pass
                    '''
                )
            )

            (temp_path / "bad.py").write_text(
                dedent(
                    """
                    def bad_function():
                        pass
                    """
                )
            )

            (temp_path / "subdir").mkdir()
            (temp_path / "subdir" / "nested.py").write_text(
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

            temp_path = Path(temp_dir)

            # Create test files
            (temp_path / "bad.py").write_text(
                dedent(
                    """
                    def bad_function():
                        pass
                    """
                )
            )

            (temp_path / "subdir").mkdir()
            (temp_path / "subdir" / "nested.py").write_text(
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

            temp_path = Path(temp_dir)

            # Create test files
            (temp_path / "good.py").write_text(
                dedent(
                    '''
                    def good_function():
                        """Good docstring."""
                        pass
                    '''
                )
            )
            (temp_path / "test_bad.py").write_text(
                dedent(
                    """
                    def bad_function():
                        pass
                    """
                )
            )

            (temp_path / "regular_bad.py").write_text(
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

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:

            f.write(python_content)
            f.flush()

            with pytest.raises(SyntaxError):
                self.simple_checker.check_file(f.name)

            Path(f.name).unlink()

    def test_09_check_non_python_file(self) -> None:
        """
        Test error handling for non-Python files.
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:

            f.write("This is not a Python file")
            f.flush()

            with pytest.raises(ValueError):
                self.simple_checker.check_file(f.name)

            Path(f.name).unlink()

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
                """This should be checked."""
                pass
            '''
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:

            f.write(python_content)
            f.flush()

            errors: list[DocstringError] = self.simple_checker.check_file(f.name)
            # Should only check public_function, ignore private ones
            assert len(errors) == 0

            Path(f.name).unlink()
