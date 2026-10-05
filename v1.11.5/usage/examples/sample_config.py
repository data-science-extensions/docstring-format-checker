def my_function(param1: int, param2: str = "default") -> bool:
    """
    !!! note "Summary"
        This is a function with a summary in an admonition.

    Params:
        param1 (int): The first parameter.
        param2 (str): The second parameter.

    Returns:
        (bool): Success or failure.
    """
    return True


def _private_function():
    """
    This is a private function.
    """
    pass


def undocumented_function():
    pass
