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
from typing import Optional
from unittest import TestCase
from unittest.mock import MagicMock, patch

# ## Python Third Party Imports ----
import pytest
from pytest import raises

# ## Local First Party Imports ----
from docstring_format_checker.config import SectionConfig, find_config_file, load_config
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
        config: list[SectionConfig] = load_config()
        assert len(config) > 0
        assert all(isinstance(section, SectionConfig) for section in config)
        assert any(section.name == "summary" for section in config)

    def test_02_load_config_from_toml(self) -> None:

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

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=True) as f:

            f.write(toml_content)
            f.flush()

            config: list[SectionConfig] = load_config(f.name)
            assert len(config) == 2
            assert config[0].name == "summary"
            assert config[1].name == "params"

    def test_03_load_config_alternative_table_name(self) -> None:

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

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=True) as f:

            f.write(toml_content)
            f.flush()

            config: list[SectionConfig] = load_config(f.name)
            assert len(config) == 1
            assert config[0].name == "test"

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

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=True) as f:

            # Write invalid TOML content
            f.write("invalid toml [[[syntax")
            f.flush()

            with raises(InvalidConfigError, match="Failed to parse TOML file"):
                load_config(f.name)

    def test_08_load_config_missing_tool_section(self) -> None:
        """
        Test loading config when [tool.dfc] section doesn't exist.
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=True) as f:

            # Write TOML without tool.dfc section
            f.write(
                dedent(
                    """
                    [build-system]
                    requires = ["setuptools", "wheel"]

                    [tool.other]
                    setting = "value"
                    """
                ).strip()
            )

            f.flush()

            # Should return default config when no dfc section found
            config: list[SectionConfig] = load_config(f.name)
            assert isinstance(config, list)
            assert len(config) > 0  # DEFAULT_CONFIG has sections

    def test_09_load_config_missing_sections_array(self) -> None:
        """
        Test loading config when sections array is missing.
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=True) as f:

            # Write TOML with tool.dfc but no sections
            f.write(
                dedent(
                    """
                    [tool.dfc]
                    some_setting = "value"
                    """
                ).strip()
            )

            f.flush()

            # Should return default config when no sections found
            config: list[SectionConfig] = load_config(f.name)
            assert isinstance(config, list)
            assert len(config) > 0  # Returns DEFAULT_CONFIG (has 8 sections)

    def test_10_section_config_validation_errors(self) -> None:
        """
        Test SectionConfig validation with various error conditions.
        """

        # Test invalid section creation through load_config with bad data
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=True) as f:

            # Missing required fields
            f.write(
                dedent(
                    """
                    [tool.dfc]

                    [[tool.dfc.sections]]
                    name = "test"
                    # Missing order, type, required
                    """
                ).strip()
            )

            f.flush()

            with raises(InvalidConfigError, match="Invalid section configuration"):
                load_config(f.name)

        # Test section with invalid type through config loading
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=True) as f:

            f.write(
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

            f.flush()

            with raises(InvalidConfigError, match="Invalid section configuration"):
                load_config(f.name)

    def test_11_alternative_config_file_discovery(self) -> None:
        """
        Test pyproject.toml config file discovery.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            temp_path = Path(temp_dir)

            # Create pyproject.toml file with dfc config
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

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=True) as f:

            f.write(
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

            f.flush()

            # This should work regardless of Python version
            config: list[SectionConfig] = load_config(f.name)
            assert len(config) == 1
            assert config[0].name == "summary"

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
                assert isinstance(config, list)
                assert len(config) > 0  # DEFAULT_CONFIG has sections
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

            temp_path = Path(temp_dir)

            # Create a malformed pyproject.toml
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

        # Test the validation function directly
        # ## Local First Party Imports ----
        from docstring_format_checker.config import _validate_config_order

        # Create config sections with duplicate orders
        sections = [
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

        # Test the validation function directly
        # ## Local First Party Imports ----
        from docstring_format_checker.config import _validate_config_order

        # Create config sections with multiple duplicate orders
        sections = [
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

        # Test the validation function directly
        # ## Local First Party Imports ----
        from docstring_format_checker.config import _validate_config_order

        # Create config sections with unique orders
        sections = [
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
