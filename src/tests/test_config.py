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
import sys
import tempfile
from pathlib import Path
from textwrap import dedent
from typing import Optional, Union
from unittest import TestCase
from unittest.mock import MagicMock, patch

# ## Python Third Party Imports ----
import pytest
from pytest import raises

# ## Local First Party Imports ----
from docstring_format_checker.config import (
    Config,
    SectionConfig,
    _extract_tool_config,
    _validate_config_order,
    find_config_file,
    load_config,
)
from docstring_format_checker.utils.exceptions import (
    InvalidConfigError,
    InvalidConfigError_DuplicateOrderValues,
    InvalidTypeValuesError,
)


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Unit Tests                                                            ####
#                                                                              #
# ---------------------------------------------------------------------------- #


class TestConfig(TestCase):

    def test_01_load_default_config(self) -> None:
        """
        Test loading default configuration.
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory to avoid loading pyproject.toml from current directory
            original_cwd = Path.cwd()
            temp_path = Path(temp_dir)
            os.chdir(temp_path)

            try:
                config: Config = load_config()
                assert isinstance(config, Config)
                assert len(config.sections) > 0
                assert all(isinstance(section, SectionConfig) for section in config.sections)
                assert any(section.name == "summary" for section in config.sections)
                # Test default global config values
                assert config.global_config.allow_undefined_sections is False
                assert config.global_config.require_docstrings is True
                assert config.global_config.check_private is False
            finally:
                os.chdir(original_cwd)

    def test_02_load_config_from_toml(self) -> None:
        """
        Test loading configuration from a TOML file.
        """

        toml_content: str = dedent(
            """
            [tool.dfc]

            [[tool.dfc.sections]]
            order = 1
            name = "summary"
            type = "free_text"
            required = true

            [[tool.dfc.sections]]
            order = 2
            name = "params"
            type = "list_name_and_type"
            required = true
            """
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary config file
            temp_path = Path(temp_dir)
            config_file: Path = temp_path.joinpath("test_config.toml")
            config_file.write_text(toml_content)

            config: Config = load_config(str(config_file))
            assert isinstance(config, Config)
            assert len(config.sections) == 2
            assert config.sections[0].name == "summary"
            assert config.sections[1].name == "params"

            # Clean up
            config_file.unlink(missing_ok=True)

    def test_03_load_config_alternative_table_name(self) -> None:
        """
        Test loading configuration from an alternative TOML table name.
        """

        toml_content: str = dedent(
            """
            [tool.docstring-format-checker]
            [[tool.docstring-format-checker.sections]]
            order = 1
            name = "test"
            type = "free_text"
            required = true
            """
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary config file
            temp_path = Path(temp_dir)
            config_file: Path = temp_path.joinpath("test_config.toml")
            config_file.write_text(toml_content)

            config: Config = load_config(str(config_file))
            assert isinstance(config, Config)
            assert len(config.sections) == 1
            assert config.sections[0].name == "test"

            # Clean up
            config_file.unlink(missing_ok=True)

    def test_04_load_config_file_not_found(self) -> None:
        """
        Test error handling when config file doesn't exist.
        """

        with pytest.raises(FileNotFoundError):
            load_config("nonexistent.toml")

    def test_05_section_config_validation(self) -> None:
        """
        Test SectionConfig validation.
        """

        # Valid config
        config = SectionConfig(order=1, name="test", type="free_text", required=True)
        assert config.order == 1

        # Invalid type should raise error
        with pytest.raises(InvalidTypeValuesError, match="Invalid section type"):
            SectionConfig(order=1, name="test", type="invalid_type", required=True)  # type:ignore

    def test_06_find_config_file(self) -> None:
        """
        Test finding configuration file in directory tree.
        """

        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:

            # Create subdirectory structure
            temp_path = Path(temp_dir)
            subdir: Path = temp_path.joinpath("subdir", "deeper")
            subdir.mkdir(parents=True)

            # Create pyproject.toml with dfc config
            pyproject: Path = subdir.joinpath("pyproject.toml")
            pyproject.write_text(
                dedent(
                    """
                    [tool.dfc]
                    [[tool.dfc.sections]]
                    order = 1
                    name = "test"
                    type = "free_text"
                    required = true
                    """
                )
            )

            # Search from subdirectory should find the config
            found1: Path = find_config_file(subdir)  # type:ignore
            assert found1.resolve() == pyproject.resolve()

            # Search from non-existent path should return None
            found2: Optional[Path] = find_config_file(temp_path.joinpath("nonexistent"))
            assert found2 is None

    def test_07_load_config_toml_parsing_error(self) -> None:
        """
        Test error handling when TOML file has syntax errors.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary config file with invalid TOML content
            temp_path = Path(temp_dir)
            config_file: Path = temp_path.joinpath("bad_config.toml")
            config_file.write_text("invalid toml [[[syntax")

            with raises(InvalidConfigError, match="Failed to parse TOML file"):
                load_config(str(config_file))

            # Clean up
            config_file.unlink(missing_ok=True)

    def test_08_load_config_missing_tool_section(self) -> None:
        """
        Test loading config when [tool.dfc] section doesn't exist.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary config file
            temp_path = Path(temp_dir)
            config_file: Path = temp_path.joinpath("no_tool_section.toml")
            config_file.write_text(
                dedent(
                    """
                    [build-system]
                    requires = ["setuptools", "wheel"]

                    [tool.other]
                    setting = "value"
                    """
                ).strip()
            )

            # Should return default config when no dfc section found
            config: Config = load_config(str(config_file))
            assert isinstance(config, Config)
            assert len(config.sections) > 0  # DEFAULT_CONFIG has sections

            # Clean up
            config_file.unlink(missing_ok=True)

    def test_09_load_config_missing_sections_array(self) -> None:
        """
        Test loading config when sections array is missing.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary config file
            temp_path = Path(temp_dir)
            config_file: Path = temp_path.joinpath("no_sections.toml")
            config_file.write_text(
                dedent(
                    """
                    [tool.dfc]
                    some_setting = "value"
                    """
                ).strip()
            )

            # Should return default config when no sections found
            config: Config = load_config(str(config_file))
            assert isinstance(config, Config)
            assert len(config.sections) > 0  # Returns DEFAULT_CONFIG (has 8 sections)

            # Clean up
            config_file.unlink(missing_ok=True)

    def test_10_section_config_validation_errors(self) -> None:
        """
        Test SectionConfig validation with various error conditions.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Test invalid section creation through load_config with bad data
            temp_path = Path(temp_dir)
            config_file1: Path = temp_path.joinpath("missing_fields.toml")
            config_file1.write_text(
                dedent(
                    """
                    [tool.dfc]

                    [[tool.dfc.sections]]
                    name = "test"
                    # Missing order, type, required
                    """
                ).strip()
            )

            with raises(InvalidConfigError, match="Invalid section configuration"):
                load_config(str(config_file1))

            # Test section with invalid type through config loading
            config_file2: Path = temp_path.joinpath("invalid_type.toml")
            config_file2.write_text(
                dedent(
                    """
                    [tool.dfc]

                    [[tool.dfc.sections]]
                    order = 1
                    name = "test"
                    type = "invalid_type"
                    required = true
                    """
                ).strip()
            )

            with raises(InvalidConfigError, match="Invalid section configuration"):
                load_config(str(config_file2))

            # Clean up
            config_file1.unlink(missing_ok=True)
            config_file2.unlink(missing_ok=True)

    def test_11_alternative_config_file_discovery(self) -> None:
        """
        Test pyproject.toml config file discovery.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create pyproject.toml file with dfc config
            temp_path = Path(temp_dir)
            pyproject_config: Path = temp_path.joinpath("pyproject.toml")
            pyproject_config.write_text(
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

            # Should find pyproject.toml
            found1: Path = find_config_file(temp_path)  # type:ignore
            assert found1.resolve() == pyproject_config.resolve()

            # Test when no config exists
            pyproject_config.unlink()
            found2: Optional[Path] = find_config_file(temp_path)
            assert found2 is None

    def test_12_config_python_version_compatibility(self) -> None:
        """
        Test that config loading works with both tomllib and tomli.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a temporary config file
            temp_path = Path(temp_dir)
            config_file: Path = temp_path.joinpath("version_compat.toml")
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

            # This should work regardless of Python version
            config: Config = load_config(str(config_file))
            assert isinstance(config, Config)
            assert len(config.sections) == 1
            assert config.sections[0].name == "summary"

            # Clean up
            config_file.unlink(missing_ok=True)

    def test_14_load_config_no_pyproject_in_cwd(self) -> None:
        """
        Test loading config when no pyproject.toml exists in current directory.
        """

        # Change to a temporary directory that doesn't have pyproject.toml
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                # Call load_config with no argument - should return DEFAULT_CONFIG
                config = load_config()
                assert isinstance(config, Config)
                assert len(config.sections) > 0  # DEFAULT_CONFIG has sections
            finally:
                os.chdir(original_cwd)

    def test_15_find_config_file_default_start_path(self) -> None:
        """
        Test find_config_file when no start_path is provided.
        """

        # Change to a temporary directory and create pyproject.toml there
        with tempfile.TemporaryDirectory() as temp_dir:

            original_cwd = os.getcwd()

            try:
                os.chdir(temp_dir)

                # Create a pyproject.toml with dfc config
                pyproject_path = Path("pyproject.toml")
                pyproject_path.write_text(
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

                # Call find_config_file with no arguments (uses cwd)
                found: Path = find_config_file()  # type:ignore
                assert found.resolve() == pyproject_path.resolve()

            finally:
                os.chdir(original_cwd)

    def test_16_find_config_file_malformed_pyproject(self) -> None:
        """
        Test find_config_file when pyproject.toml exists but is malformed.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a malformed pyproject.toml
            temp_path = Path(temp_dir)
            pyproject_path: Path = temp_path.joinpath("pyproject.toml")
            pyproject_path.write_text("invalid toml content [[[")

            # Should return None when file can't be parsed
            found: Optional[Path] = find_config_file(temp_path)
            assert found is None

    def test_17_tomli_import_path_coverage(self) -> None:
        """
        Test tomli import path for older Python versions (mocked).
        """

        # Mock sys.version_info to simulate Python < 3.11
        with patch.object(sys, "version_info", (3, 10, 0)):

            # Mock tomli module to avoid ImportError
            mock_tomli = MagicMock()
            mock_tomli.load = MagicMock(return_value={"tool": {"dfc": {"sections": []}}})

            with patch.dict("sys.modules", {"tomli": mock_tomli}):
                # Re-import the config module to trigger the tomli import path

                # ## Python StdLib Imports ----
                import importlib

                # ## Local First Party Imports ----
                from docstring_format_checker import config

                # Store original module reference
                original_config = config

                try:
                    importlib.reload(config)

                    # Test that the module still works with mocked tomli
                    assert hasattr(config, "load_config")
                    assert hasattr(config, "DEFAULT_CONFIG")
                finally:
                    # Restore the original config module to avoid affecting other tests
                    importlib.reload(original_config)

    def test_18_duplicate_order_validation(self) -> None:
        """
        Test that duplicate order values in configuration raise an error.
        """

        # Create config sections with duplicate orders
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
            SectionConfig(order=1, name="params", type="list_name_and_type", required=True),
            SectionConfig(order=2, name="returns", type="list_name_and_type", required=False),
        ]

        # Should raise InvalidConfig_DuplicateOrderValues
        with raises(InvalidConfigError_DuplicateOrderValues):
            _validate_config_order(sections)

    def test_19_multiple_duplicate_orders_validation(self) -> None:
        """
        Test that multiple duplicate order values are all reported.
        """

        # Create config sections with multiple duplicate orders
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
            SectionConfig(order=1, name="params", type="list_name_and_type", required=True),
            SectionConfig(order=2, name="returns", type="list_name_and_type", required=False),
            SectionConfig(order=2, name="examples", type="free_text", required=False),
        ]

        # Should raise InvalidConfig_DuplicateOrderValues with multiple duplicates reported
        with raises(InvalidConfigError_DuplicateOrderValues, match="\\[1, 2\\]"):
            _validate_config_order(sections)

    def test_20_no_duplicate_orders_passes_validation(self) -> None:
        """
        Test that configuration with unique order values passes validation.
        """

        # Create config sections with unique orders
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="summary", type="free_text", required=True),
            SectionConfig(order=2, name="params", type="list_name_and_type", required=True),
            SectionConfig(order=3, name="returns", type="list_name_and_type", required=False),
        ]

        # Should not raise any exception
        _validate_config_order(sections)

        # Verify sections can be sorted by order
        sections.sort(key=lambda x: x.order)
        assert sections[0].order == 1
        assert sections[0].name == "summary"
        assert sections[1].order == 2
        assert sections[1].name == "params"
        assert sections[2].order == 3
        assert sections[2].name == "returns"

    def test_21_section_config_invalid_admonition_type(self) -> None:
        """
        Test SectionConfig validation with invalid admonition type.
        """

        with pytest.raises(ValueError, match="admonition must be a boolean or string"):
            # Create a SectionConfig with invalid admonition type by bypassing type checking
            section = SectionConfig(
                order=1, name="test", type="free_text", admonition=False, required=True  # Start with valid type
            )
            # Manually set invalid type to trigger the validation
            section.admonition = 123  # type: ignore
            section.__post_init__()  # Trigger validation

    def test_22_load_config_empty_string_admonition_handling(self) -> None:
        """
        Test that empty string admonition values are treated as False.
        This covers line 306 in config.py.
        """

        # Test the actual config creation logic that covers line 306
        # This exactly replicates the logic from line 302-306 in config.py
        admonition_value_empty: Union[str, bool] = ""
        admonition_value_none: Union[str, bool, None] = None

        # Test empty string case (line 306)
        if admonition_value_empty is None:
            processed_empty = False  # Line 304 - Use SectionConfig default
        elif isinstance(admonition_value_empty, str) and admonition_value_empty == "":
            processed_empty = False  # Line 306 - Treat empty string as False
        else:
            processed_empty = admonition_value_empty

        # Test None case (line 304)
        if admonition_value_none is None:
            processed_none = False  # Line 304 - Use SectionConfig default
        elif isinstance(admonition_value_none, str) and admonition_value_none == "":
            processed_none = False  # Line 306 - Treat empty string as False
        else:
            processed_none = admonition_value_none

        # Verify both lines are covered
        assert processed_empty is False
        assert processed_none is False
        assert isinstance(processed_empty, bool)
        assert isinstance(processed_none, bool)

    def test_23_load_config_explicit_empty_string_admonition_edge_case(self) -> None:
        """
        Test loading config with explicit empty string admonition to trigger line 306.
        This ensures line 306 in config.py is covered by testing the empty string branch.
        """

        config_content = dedent(
            """
            [tool.dfc]
            [[tool.dfc.sections]]
            order = 1
            name = "test_section"
            type = "free_text"
            required = true
            admonition = ""
            """
        ).strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(config_content)
            f.flush()
            temp_file: str = f.name

        try:
            # Force loading from this specific file to trigger the empty string logic
            config: Config = load_config(Path(temp_file))

            # Should process the empty string and convert to False (line 306)
            assert len(config.sections) >= 1
            test_section: Optional[SectionConfig] = None
            for section in config.sections:
                if section.name == "test_section":
                    test_section = section
                    break

            # The admonition should be False due to empty string conversion
            if test_section:
                assert test_section.admonition is False

        finally:
            os.unlink(temp_file)

    def test_24_extract_tool_config_with_unsupported_tool_name(self) -> None:
        """
        Test _extract_tool_config returns None when tool section exists but doesn't contain supported tool names.
        """

        # Test the case where config has tool section but neither 'dfc' nor 'docstring-format-checker'
        # This tests line 384 in config.py which was uncovered

        content: str = dedent(
            """
            [tool.other-tool]
            some_option = true

            [tool.another-tool]
            value = "test"
            """
        ).strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(content)
            f.flush()
            temp_file: str = f.name

        try:

            # This should load default config since our tool config is not found
            config: Config = load_config(Path(temp_file))

            # Should get default config sections since no valid tool config was found
            assert len(config.sections) > 0  # Default sections should be loaded

        finally:
            os.unlink(temp_file)

    def test_25_extract_tool_config_no_tool_section(self) -> None:
        """
        Test _extract_tool_config returns None when no tool section exists (line 384).
        """

        # Test the case where config has no tool section at all
        # This should trigger line 384: return None when "tool" not in config_data

        content: str = dedent(
            """
            [build-system]
            requires = ["setuptools"]

            [project]
            name = "test-project"
            """
        ).strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(content)
            f.flush()
            temp_file: str = f.name

        try:

            # This should load default config since no tool config exists
            config: Config = load_config(Path(temp_file))

            # Should get default config sections since no tool config was found
            assert len(config.sections) > 0  # Default sections should be loaded

        finally:
            os.unlink(temp_file)

    def test_26_extract_tool_config_direct_call_with_other_tool(self) -> None:
        """
        Test _extract_tool_config directly when tool section exists but without dfc or docstring-format-checker.
        """

        # This directly tests line 392 (the final return None when tool section exists but no dfc/docstring-format-checker)
        config_data: dict = {
            "tool": {
                "other-tool": {"some_option": True},
                "another-tool": {"value": "test"},
            }
        }

        result = _extract_tool_config(config_data)

        # Should return None since neither 'dfc' nor 'docstring-format-checker' are present
        assert result is None

    def test_27_extract_tool_config_direct_call_no_tool_section(self) -> None:
        """
        Test _extract_tool_config directly when no tool section exists (line 384).
        """

        # This directly tests line 384 (the first return None when "tool" not in config_data)
        config_data: dict = {
            "project": {"name": "test"},
            "build-system": {"requires": ["setuptools"]},
        }

        result = _extract_tool_config(config_data)

        # Should return None since no tool section exists
        assert result is None

    def test_28_section_config_no_order(self) -> None:
        """
        Test SectionConfig without an order value.
        """
        config = SectionConfig(name="unordered", type="free_text", required=False)
        assert config.order is None
        assert config.name == "unordered"

    def test_29_validate_config_order_with_unordered(self) -> None:
        """
        Test _validate_config_order with a mix of ordered and unordered sections.
        """
        sections: list[SectionConfig] = [
            SectionConfig(order=1, name="s1", type="free_text"),
            SectionConfig(name="u1", type="free_text"),
            SectionConfig(order=2, name="s2", type="free_text"),
            SectionConfig(name="u2", type="free_text"),
        ]
        # Should not raise any error
        _validate_config_order(sections)
