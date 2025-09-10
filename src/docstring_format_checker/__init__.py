"""
Docstring Format Checker.

A CLI tool to check and validate Python docstring formatting and completeness.
"""

__version__ = "v1.0.0"
__author__ = "Chris Mahoney"
__email__ = "docstring-format-checker@data-science-extensions.com"


# ## Local First Party Imports ----
from docstring_format_checker.config import DEFAULT_CONFIG, load_config
from docstring_format_checker.core import DocstringChecker, SectionConfig


__all__: list[str] = [
    "DocstringChecker",
    "SectionConfig",
    "load_config",
    "DEFAULT_CONFIG",
]
