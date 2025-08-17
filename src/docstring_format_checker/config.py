# ============================================================================ #
#                                                                              #
#     Title: Configuration Management                                         #
#     Purpose: Configuration for docstring format checking                    #
#     Notes: Notes                                                             #
#     Author: chrimaho                                                         #
#     Created: Created                                                         #
#     References: References                                                   #
#     Sources: Sources                                                         #
#     Edited: Edited                                                           #
#                                                                              #
# ============================================================================ #


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Overview                                                              ####
#                                                                              #
# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
#  Description                                                              ####
# ---------------------------------------------------------------------------- #


"""
!!! note "Summary"
    Configuration handling for the docstring format checker.
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
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Optional, Union


if sys.version_info >= (3, 11):
    # ## Python StdLib Imports ----
    import tomllib
else:
    # ## Python Third Party Imports ----
    import tomli as tomllib


# (No local imports needed)


## --------------------------------------------------------------------------- #
##  Exports                                                                 ####
## --------------------------------------------------------------------------- #


__all__: list[str] = ["SectionConfig", "DEFAULT_CONFIG", "load_config", "find_config_file"]


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Helpers                                                               ####
#                                                                              #
# ---------------------------------------------------------------------------- #


## --------------------------------------------------------------------------- #
##  Classes                                                                 ####
## --------------------------------------------------------------------------- #


@dataclass
class SectionConfig:
    """
    Configuration for a docstring section.
    """

    order: int
    name: str
    type: Literal["free_text", "list_name", "list_type", "list_name_and_type"]
    admonition: str = ""
    prefix: str = ""  # Support any prefix string
    required: bool = False
    message: str = ""  # Optional message for validation errors

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        VALID_TYPES: list[str] = [
            "free_text",  # Free text sections (summary, details, examples, notes)
            "list_name",  # Simple name sections (name)
            "list_type",  # Simple type sections (raises, yields)
            "list_name_and_type",  # Params-style sections (name (type): description)
        ]
        if self.type not in VALID_TYPES:


## --------------------------------------------------------------------------- #
##  Validations                                                             ####
## --------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Main Section                                                          ####
#                                                                              #
# ---------------------------------------------------------------------------- #


DEFAULT_CONFIG: list[SectionConfig] = [
    SectionConfig(
        order=1,
        name="summary",
        type="free_text",
        admonition="note",
        prefix="!!!",
        required=True,
    ),
    SectionConfig(
        order=2,
        name="details",
        type="free_text",
        admonition="info",
        prefix="???+",
        required=False,
    ),
    SectionConfig(
        order=3,
        name="params",
        type="list_name_and_type",
        required=True,
    ),
    SectionConfig(
        order=4,
        name="returns",
        type="list_name_and_type",
        required=False,
    ),
    SectionConfig(
        order=5,
        name="yields",
        type="list_type",
        required=False,
    ),
    SectionConfig(
        order=6,
        name="raises",
        type="list_type",
        required=False,
    ),
    SectionConfig(
        order=7,
        name="examples",
        type="free_text",
        admonition="example",
        prefix="???+",
        required=False,
    ),
    SectionConfig(
        order=8,
        name="notes",
        type="free_text",
        admonition="note",
        prefix="???",
        required=False,
    ),
]


def load_config(config_path: Optional[Union[str, Path]] = None) -> list[SectionConfig]:
    """
    Load configuration from a TOML file or return default configuration.

    Args:
        config_path:
            Path to the TOML configuration file. If None, looks for pyproject.toml in current directory.

    Returns:
        List of SectionConfig objects defining the docstring sections to check.

    Raises:
        FileNotFoundError:
            If the specified config file doesn't exist.
        ValueError:
            If the configuration is invalid.
    """
    if config_path is None:
        # Look for pyproject.toml in current directory
        pyproject_path: Path = Path.cwd() / "pyproject.toml"
        if pyproject_path.exists():
            config_path = pyproject_path
        else:
            return DEFAULT_CONFIG

    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path, "rb") as f:
            config_data: dict[str, Any] = tomllib.load(f)
    except Exception as e:
        raise ValueError(f"Failed to parse TOML file {config_path}: {e}") from e

    # Try to find configuration under [tool.dfc] or [tool.docstring-format-checker]
    tool_config = None
    if "tool" in config_data:
        if "dfc" in config_data["tool"]:
            tool_config = config_data["tool"]["dfc"]
        elif "docstring-format-checker" in config_data["tool"]:
            tool_config = config_data["tool"]["docstring-format-checker"]

    if tool_config is None:
        return DEFAULT_CONFIG

    # Parse sections configuration
    sections_config: list[SectionConfig] = []
    if "sections" in tool_config:
        sections_data = tool_config["sections"]
        for section_data in sections_data:
            try:
                section = SectionConfig(
                    order=section_data.get("order", 0),
                    name=section_data.get("name", ""),
                    type=section_data.get("type", ""),
                    admonition=section_data.get("admonition", ""),
                    prefix=section_data.get("prefix", ""),
                    required=section_data.get("required", False),
                )
                sections_config.append(section)
            except (KeyError, TypeError, ValueError) as e:
                raise ValueError(f"Invalid section configuration: {section_data}. Error: {e}") from e

    if not sections_config:
        return DEFAULT_CONFIG

    # Sort by order
    sections_config.sort(key=lambda x: x.order)

    return sections_config


def find_config_file(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Find configuration file by searching up the directory tree.

    Args:
        start_path:
            Directory to start searching from. Defaults to current directory.

    Returns:
        Path to the configuration file if found, None otherwise.
    """
    if start_path is None:
        start_path = Path.cwd()

    current_path: Path = start_path.resolve()

    while current_path != current_path.parent:
        pyproject_path: Path = current_path / "pyproject.toml"
        if pyproject_path.exists():
            # Check if it contains dfc configuration
            try:
                with open(pyproject_path, "rb") as f:
                    config_data: dict[str, Any] = tomllib.load(f)
                    if "tool" in config_data and (
                        "dfc" in config_data["tool"] or "docstring-format-checker" in config_data["tool"]
                    ):
                        return pyproject_path
            except Exception:
                pass

        current_path = current_path.parent

    return None
