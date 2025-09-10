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
        self.message = message
        self.file_path = file_path
        self.line_number = line_number
        self.item_name = item_name
        self.item_type = item_type
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
