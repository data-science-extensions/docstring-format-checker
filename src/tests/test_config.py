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
from docstring_format_checker.config import SectionConfig, find_config_file, load_config


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Unit Tests                                                            ####
#                                                                              #
# ---------------------------------------------------------------------------- #


class TestConfig(TestCase):

    def test_01_load_default_config(self) -> None:
        """Test loading default configuration."""
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

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:

            f.write(toml_content)
            f.flush()

            config: list[SectionConfig] = load_config(f.name)
            assert len(config) == 2
            assert config[0].name == "summary"
            assert config[1].name == "params"

            Path(f.name).unlink()

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

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:

            f.write(toml_content)
            f.flush()

            config: list[SectionConfig] = load_config(f.name)
            assert len(config) == 1
            assert config[0].name == "test"

            Path(f.name).unlink()

    def test_04_load_config_file_not_found(self) -> None:
        """Test error handling when config file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent.toml")

    def test_05_section_config_validation(self) -> None:
        """Test SectionConfig validation."""
        # Valid config
        config = SectionConfig(order=1, name="test", type="free_text", required=True)
        assert config.order == 1

        # Invalid type should raise error
        with pytest.raises(ValueError):
            SectionConfig(order=1, name="test", type="invalid_type", required=True)

    def test_06_find_config_file(self) -> None:
        """Test finding configuration file in directory tree."""

        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:

            temp_path = Path(temp_dir)
            subdir: Path = temp_path / "subdir" / "deeper"
            subdir.mkdir(parents=True)

            # Create pyproject.toml with dfc config
            pyproject: Path = subdir / "pyproject.toml"
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
            found: Path | None = find_config_file(subdir)
            assert found == pyproject

            # Search from non-existent path should return None
            found: Path | None = find_config_file(temp_path / "nonexistent")
            assert found is None
