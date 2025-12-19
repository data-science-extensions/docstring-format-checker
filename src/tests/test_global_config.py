# ---------------------------------------------------------------------------- #
#                                                                              #
#     Test Global Config Features                                           ####
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

# ## Local First Party Imports ----
from docstring_format_checker.config import (
    Config,
    GlobalConfig,
    SectionConfig,
    load_config,
)
from docstring_format_checker.core import DocstringChecker
from docstring_format_checker.utils.exceptions import DocstringError


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Test Global Config Features                                           ####
#                                                                              #
# ---------------------------------------------------------------------------- #


class TestGlobalConfigFeatures(TestCase):
    """
    Test the new global configuration flags.
    """

    def test_load_global_config_from_toml(self) -> None:
        """
        Test loading global config flags from TOML file.
        """

        toml_content: str = dedent(
            """
            [tool.dfc]
            allow_undefined_sections = true
            require_docstrings = false
            check_private = true

            [[tool.dfc.sections]]
            order = 1
            name = "summary"
            type = "free_text"
            required = true
            """
        ).strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()
            temp_file: str = f.name

        try:
            # Force module reload to avoid potential caching issues
            # ## Python StdLib Imports ----
            import importlib

            if "docstring_format_checker.config" in sys.modules:
                importlib.reload(sys.modules["docstring_format_checker.config"])

            config: Config = load_config(temp_file)

            # Verify global config was loaded correctly
            assert config.global_config.allow_undefined_sections is True
            assert config.global_config.require_docstrings is False
            assert config.global_config.check_private is True

            # Verify sections were loaded correctly
            assert len(config.sections) == 1
            assert config.sections[0].name == "summary"

        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_load_default_global_config_values(self) -> None:
        """
        Test that default global config values are used when not specified in TOML.
        """

        toml_content: str = dedent(
            """
            [tool.dfc]

            [[tool.dfc.sections]]
            order = 1
            name = "summary"
            type = "free_text"
            required = true
            """
        ).strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()
            temp_file: str = f.name

        try:

            config: Config = load_config(temp_file)

            # Verify default global config values
            assert config.global_config.allow_undefined_sections is False
            assert config.global_config.require_docstrings is True
            assert config.global_config.check_private is False

        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_allow_undefined_sections_false(self) -> None:
        """
        Test that undefined sections raise errors when allow_undefined_sections=False.
        """

        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
        ]

        # Default behavior: undefined sections should cause errors
        config = Config(global_config=GlobalConfig(allow_undefined_sections=False), sections=sections)
        checker = DocstringChecker(config)

        # Create a Python file with an undefined section
        python_content: str = dedent(
            '''
            def test_function():
                """
                !!! note "Summary"
                    This is a summary.

                Undefined_Section:
                    This section is not defined in config.
                """
                pass
            '''
        ).strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(python_content)
            f.flush()
            temp_file = f.name

        try:
            errors: list[DocstringError] = checker.check_file(temp_file)
            # Should have an error about the undefined section
            assert len(errors) > 0
            error_messages: list[str] = [e.message for e in errors]
            assert any("undefined_section" in msg.lower() for msg in error_messages)

        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_allow_undefined_sections_true(self) -> None:
        """
        Test that undefined sections are ignored when allow_undefined_sections=True.
        """

        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
        ]

        # Allow undefined sections
        config = Config(global_config=GlobalConfig(allow_undefined_sections=True), sections=sections)
        checker = DocstringChecker(config)

        # Create a Python file with an undefined section
        python_content: str = dedent(
            '''
            def test_function():
                """
                !!! note "Summary"
                    This is a summary.

                Undefined_Section:
                    This section is not defined in config.
                """
                pass
            '''
        ).strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(python_content)
            f.flush()
            temp_file: str = f.name

        try:
            errors: list[DocstringError] = checker.check_file(temp_file)
            # Should NOT have errors about undefined sections
            error_messages: list[str] = [e.message for e in errors]
            assert not any("undefined_section" in msg.lower() for msg in error_messages)

        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_require_docstrings_true(self) -> None:
        """
        Test that missing docstrings raise errors when require_docstrings=True.
        """

        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
        ]

        # Default behavior: require docstrings
        config = Config(global_config=GlobalConfig(require_docstrings=True), sections=sections)
        checker = DocstringChecker(config)

        # Create a Python file with a function missing docstring
        python_content: str = dedent(
            """
            def test_function():
                pass
            """
        ).strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(python_content)
            f.flush()
            temp_file = f.name

        try:
            errors: list[DocstringError] = checker.check_file(temp_file)
            # Should have an error about missing docstring
            assert len(errors) > 0
            error_messages: list[str] = [e.message for e in errors]
            assert any("missing docstring" in msg.lower() for msg in error_messages)

        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_require_docstrings_false(self) -> None:
        """
        Test that missing docstrings are ignored when require_docstrings=False.
        """

        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
        ]

        # Don't require docstrings
        config = Config(global_config=GlobalConfig(require_docstrings=False), sections=sections)
        checker = DocstringChecker(config)

        # Create a Python file with a function missing docstring
        python_content: str = dedent(
            """
            def test_function():
                pass
            """
        ).strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(python_content)
            f.flush()
            temp_file: str = f.name

        try:
            errors: list[DocstringError] = checker.check_file(temp_file)
            # Should NOT have errors about missing docstrings
            error_messages: list[str] = [e.message for e in errors]
            assert not any("missing docstring" in msg.lower() for msg in error_messages)

        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_check_private_false(self) -> None:
        """
        Test that private functions are ignored when check_private=False.
        """

        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
        ]

        # Default behavior: don't check private functions
        config = Config(global_config=GlobalConfig(check_private=False), sections=sections)
        checker = DocstringChecker(config)

        # Create a Python file with private functions missing docstrings
        python_content: str = dedent(
            """
            def _private_function():
                pass

            def __dunder_function__():
                pass
            """
        ).strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(python_content)
            f.flush()
            temp_file = f.name

        try:
            errors: list[DocstringError] = checker.check_file(temp_file)
            # Should have NO errors since private functions are ignored
            assert len(errors) == 0

        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_check_private_true(self) -> None:
        """
        Test that private functions are checked when check_private=True.
        """

        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
        ]

        # Check private functions
        config = Config(global_config=GlobalConfig(check_private=True, require_docstrings=True), sections=sections)
        checker = DocstringChecker(config)

        # Create a Python file with private functions missing docstrings
        python_content: str = dedent(
            """
            def _private_function():
                pass

            def __dunder_function__():
                pass
            """
        ).strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(python_content)
            f.flush()
            temp_file = f.name

        try:
            errors = checker.check_file(temp_file)
            # Should have errors for missing docstrings in private functions
            assert len(errors) > 0
            error_messages = [e.message for e in errors]
            assert any("missing docstring" in msg.lower() for msg in error_messages)

        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_combined_config_flags(self) -> None:
        """
        Test multiple config flags working together.
        """

        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True, admonition="note", prefix="!!!"),
        ]

        # Allow undefined sections, don't require docstrings, check private functions
        config = Config(
            global_config=GlobalConfig(allow_undefined_sections=True, require_docstrings=False, check_private=True),
            sections=sections,
        )
        checker = DocstringChecker(config)

        # Create a Python file with private function with undefined section
        python_content = dedent(
            '''
            def _private_function():
                """
                !!! note "Summary"
                    This is a summary.

                Undefined_Section:
                    This section is not defined in config.
                """
                pass

            def public_function_no_docstring():
                pass
            '''
        ).strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(python_content)
            f.flush()
            temp_file: str = f.name

        try:
            errors: list[DocstringError] = checker.check_file(temp_file)

            # Should have NO errors:
            # - Private function is checked but has docstring (no missing docstring error)
            # - Undefined section is allowed (no undefined section error)
            # - Public function without docstring is allowed (require_docstrings=False)
            assert len(errors) == 0

        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_invalid_optional_style_raises_error(self) -> None:
        """
        Test that invalid optional_style value raises InvalidConfigError.
        """
        # ## Local First Party Imports ----
        from docstring_format_checker.config import _parse_global_config
        from docstring_format_checker.utils.exceptions import InvalidConfigError

        tool_config: dict[str, str] = {"optional_style": "invalid_mode"}

        with self.assertRaises(InvalidConfigError) as context:
            _parse_global_config(tool_config)

        assert "Invalid optional_style: 'invalid_mode'" in str(context.exception)
        assert "Must be one of: silent, validate, strict" in str(context.exception)
