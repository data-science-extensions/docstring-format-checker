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

# ## Local First Party Imports ----
from docstring_format_checker.utils.exceptions import (
    InvalidConfigError,
    InvalidConfigError_DuplicateOrderValues,
    InvalidTypeValuesError,
)


if sys.version_info >= (3, 11):
    # ## Python StdLib Imports ----
    import tomllib
else:
    # ## Python Third Party Imports ----
    import tomli as tomllib


## --------------------------------------------------------------------------- #
##  Exports                                                                 ####
## --------------------------------------------------------------------------- #


__all__: list[str] = [
    "GlobalConfig",
    "SectionConfig",
    "Config",
    "DEFAULT_CONFIG",
    "load_config",
    "find_config_file",
]


## --------------------------------------------------------------------------- #
##  Constants                                                               ####
## --------------------------------------------------------------------------- #


VALID_TYPES: tuple[str, ...] = (
    "free_text",  # Free text sections (summary, details, examples, notes)
    "list_name",  # Simple name sections (name)
    "list_type",  # Simple type sections (raises, yields)
    "list_name_and_type",  # Params-style sections (name (type): description)
)


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Config                                                                ####
#                                                                              #
# ---------------------------------------------------------------------------- #


## --------------------------------------------------------------------------- #
##  GlobalConfig                                                            ####
## --------------------------------------------------------------------------- #


@dataclass
class GlobalConfig:
    """
    Global configuration for docstring checking behavior.
    """

    allow_undefined_sections: bool = False
    require_docstrings: bool = True
    check_private: bool = False


## --------------------------------------------------------------------------- #
##  SectionConfig                                                           ####
## --------------------------------------------------------------------------- #


@dataclass
class SectionConfig:
    """
    Configuration for a docstring section.
    """

    order: int
    name: str
    type: Literal["free_text", "list_name", "list_type", "list_name_and_type"]
    admonition: Union[bool, str] = False
    prefix: str = ""  # Support any prefix string
    required: bool = False
    message: str = ""  # Optional message for validation errors

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        self._validate_types()
        self._validate_admonition_prefix_combination()

    def _validate_types(self) -> None:
        """Validate the 'type' field."""
        if self.type not in VALID_TYPES:
            raise InvalidTypeValuesError(f"Invalid section type: {self.type}. Valid types: {VALID_TYPES}")

    def _validate_admonition_prefix_combination(self) -> None:
        """Validate admonition and prefix combination rules."""

        if isinstance(self.admonition, bool):
            # Rule: admonition cannot be True (only False or string)
            if self.admonition is True:
                raise ValueError(f"Section '{self.name}': admonition cannot be True, must be False or a string")

            # Rule: if admonition is False, prefix cannot be provided
            if self.admonition is False and self.prefix:
                raise ValueError(f"Section '{self.name}': when admonition=False, prefix cannot be provided")

        elif isinstance(self.admonition, str):
            # Rule: if admonition is a string, prefix must be provided
            if not self.prefix:
                raise ValueError(f"Section '{self.name}': when admonition is a string, prefix must be provided")

        else:
            raise ValueError(
                f"Section '{self.name}': admonition must be a boolean or string, got {type(self.admonition)}"
            )


## --------------------------------------------------------------------------- #
##  Validations                                                             ####
## --------------------------------------------------------------------------- #


def _validate_config_order(config_sections: list[SectionConfig]) -> None:

    # Validate no duplicate order values
    order_values: list[int] = [section.order for section in config_sections]
    seen_orders: set[int] = set()
    duplicate_orders: set[int] = set()

    for order in order_values:
        if order in seen_orders:
            duplicate_orders.add(order)
        else:
            seen_orders.add(order)

    if duplicate_orders:
        raise InvalidConfigError_DuplicateOrderValues(
            f"Configuration contains duplicate order values: {sorted(duplicate_orders)}. "
            "Each section must have a unique order value."
        )


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Config Container                                                      ####
#                                                                              #
# ---------------------------------------------------------------------------- #


@dataclass
class Config:
    """
    Complete configuration containing global settings and section definitions.
    """

    global_config: GlobalConfig
    sections: list[SectionConfig]


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Default Configuration                                                 ####
#                                                                              #
# ---------------------------------------------------------------------------- #


DEFAULT_SECTIONS: list[SectionConfig] = [
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


DEFAULT_CONFIG: Config = Config(
    global_config=GlobalConfig(),
    sections=DEFAULT_SECTIONS,
)


def load_config(config_path: Optional[Union[str, Path]] = None) -> Config:
    """
    !!! note "Summary"
        Load configuration from a TOML file or return default configuration.

    Params:
        config_path (Optional[Union[str, Path]]):
            Path to the TOML configuration file.
            If `None`, looks for `pyproject.toml` in current directory.
            Default: `None`.

    Returns:
        (Config):
            Configuration object containing global settings and section definitions.

    Raises:
        (FileNotFoundError):
            If the specified config file doesn't exist.
        (InvalidConfigError):
            If the configuration is invalid.
    """

    if config_path is None:
        # Look for pyproject.toml in current directory
        pyproject_path: Path = Path.cwd().joinpath("pyproject.toml")
        if pyproject_path.exists():
            config_path = pyproject_path
        else:
            return DEFAULT_CONFIG

    # Convert to Path object and check existence
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path, "rb") as f:
            config_data: dict[str, Any] = tomllib.load(f)
    except Exception as e:
        raise InvalidConfigError(f"Failed to parse TOML file {config_path}: {e}") from e

    # Try to find configuration under [tool.dfc] or [tool.docstring-format-checker]
    tool_config = None
    if "tool" in config_data:
        if "dfc" in config_data["tool"]:
            tool_config = config_data["tool"]["dfc"]
        elif "docstring-format-checker" in config_data["tool"]:
            tool_config = config_data["tool"]["docstring-format-checker"]

    if tool_config is None:
        return DEFAULT_CONFIG

    # Parse global configuration flags
    global_config = GlobalConfig(
        allow_undefined_sections=tool_config.get("allow_undefined_sections", False),
        require_docstrings=tool_config.get("require_docstrings", True),
        check_private=tool_config.get("check_private", False),
    )

    # Parse sections configuration
    sections_config: list[SectionConfig] = []
    if "sections" in tool_config:
        sections_data = tool_config["sections"]
        for section_data in sections_data:
            try:
                # Get admonition value with proper default handling
                admonition_value: Union[str, bool] = section_data.get("admonition")
                if admonition_value is None:
                    admonition_value = False  # Use SectionConfig default

                section = SectionConfig(
                    order=section_data.get("order", 0),
                    name=section_data.get("name", ""),
                    type=section_data.get("type", ""),
                    admonition=admonition_value,
                    prefix=section_data.get("prefix", ""),
                    required=section_data.get("required", False),
                )
                sections_config.append(section)
            except (KeyError, TypeError, ValueError, InvalidTypeValuesError) as e:
                raise InvalidConfigError(f"Invalid section configuration: {section_data}. Error: {e}") from e

    # Use default sections if none provided, otherwise validate and sort
    if not sections_config:
        sections_config = DEFAULT_SECTIONS
    else:
        # Validate no duplicate order values
        _validate_config_order(config_sections=sections_config)

        # Sort by order
        sections_config.sort(key=lambda x: x.order)

    return Config(global_config=global_config, sections=sections_config)


def find_config_file(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    !!! note "Summary"
        Find configuration file by searching up the directory tree.

    Params:
        start_path (Optional[Path]):
            Directory to start searching from.
            If `None`, resolves to current directory.
            Default: `None`.

    Returns:
        (Optional[Path]):
            Path to the configuration file if found, None otherwise.
    """
    if start_path is None:
        start_path = Path.cwd()

    current_path: Path = start_path.resolve()

    while current_path != current_path.parent:
        pyproject_path: Path = current_path.joinpath("pyproject.toml")
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
