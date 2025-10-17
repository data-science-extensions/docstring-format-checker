# ============================================================================ #
#                                                                              #
#     Title: Exceptions Module for Docstring Format Checker                    #
#     Purpose: Custom exceptions for error handling in the docstring format    #
#               checker.                                                       #
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
    This module defines custom exceptions for handling various error scenarios
"""


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Main Section                                                          ####
#                                                                              #
# ---------------------------------------------------------------------------- #


class DocstringError(Exception):
    """
    !!! note "Summary"
        Exception raised when a docstring validation error occurs.
    """

    def __init__(
        self,
        message: str,
        file_path: str,
        line_number: int,
        item_name: str,
        item_type: str,
    ) -> None:
        """
        !!! note "Summary"
            Initialize a DocstringError.
        """
        self.message: str = message
        self.file_path: str = file_path
        self.line_number: int = line_number
        self.item_name: str = item_name
        self.item_type: str = item_type
        super().__init__(f"Line {line_number}, {item_type} '{item_name}': {message}")


class InvalidConfigError(Exception):
    """
    !!! note "Summary"
        Exception raised for invalid configuration errors.
    """

    pass


class InvalidConfigError_DuplicateOrderValues(Exception):
    """
    !!! note "Summary"
        Exception raised for duplicate order values in configuration.
    """

    pass


class InvalidTypeValuesError(Exception):
    """
    !!! note "Summary"
        Exception raised for invalid type values in configuration.
    """

    pass


class InvalidFileError(OSError):
    """
    !!! note "Summary"
        Exception raised for invalid file errors.
    """

    pass


class DirectoryNotFoundError(OSError):
    """
    !!! note "Summary"
        Exception raised for directory not found errors.
    """

    pass
