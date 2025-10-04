"""
Docstring Format Checker.

A CLI tool to check and validate Python docstring formatting and completeness.
"""

# ## Python StdLib Imports ----
from importlib.metadata import metadata

# ## Local First Party Imports ----
from docstring_format_checker.config import DEFAULT_CONFIG, load_config
from docstring_format_checker.core import DocstringChecker, SectionConfig


_metadata = metadata("docstring-format-checker")
__name__: str = _metadata["Name"]
__version__: str = _metadata["Version"]
__author__: str = _metadata["Author"]
__email__: str = _metadata.get("Email", "")

__all__: list[str] = [
    "DocstringChecker",
    "SectionConfig",
    "load_config",
    "DEFAULT_CONFIG",
]
