class DocstringError(Exception):
    """
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
        self.message = message
        self.file_path = file_path
        self.line_number = line_number
        self.item_name = item_name
        self.item_type = item_type
        super().__init__(f"Line {line_number}, {item_type} '{item_name}': {message}")


class InvalidConfigError(Exception):
    pass


class InvalidConfigError_DuplicateOrderValues(Exception):
    pass


class InvalidTypeValuesError(Exception):
    pass


class InvalidFileError(OSError):
    pass


class DirectoryNotFoundError(OSError):
    pass
