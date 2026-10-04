"""Examples of invalid docstrings for the post-deployment DFC smoke test."""


def missing_docstring() -> None:
    pass


def missing_summary(value: int) -> None:
    """
    An unmarked summary does not match the configured admonition format.

    Params:
        value (int):
            A value with a valid parameter entry.
    """


def parameter_mismatch(expected: int) -> None:
    """
    !!! note "Summary"
        Document the wrong parameter name.

    Params:
        unexpected (str):
            This name does not match the function signature.
    """


def wrong_parameter_type(value: int) -> None:
    """
    !!! note "Summary"
        Use a parameter type that does not match the annotation.

    Params:
        value (str):
            This documented type is incorrect.
    """


def undocumented_type(value: int) -> None:
    """
    !!! note "Summary"
        Omit the annotated parameter type.

    Params:
        value ():
            The type entry is malformed.
    """


def unannotated_type(value) -> None:
    """
    !!! note "Summary"
        Document a type absent from the signature.

    Params:
        value (int):
            The parameter has no signature annotation.
    """


def invalid_optional_suffix(value: int, limit: int = 1) -> None:
    """
    !!! note "Summary"
        Use optional suffixes inconsistently.

    Params:
        value (int, optional):
            This required parameter is marked optional.
        limit (int):
            This defaulted parameter is not marked optional.
    """


def invalid_sections(value: int) -> None:
    """
    !!! warning "Summary:"
        Use an incorrect admonition and an invalid colon.

    !!! warning "Details"
        Use the wrong admonition for a configured section.

    returns:
        (int):
            Use a lowercase section name.

    Params
        value int:
            Omit the heading colon and type parentheses.

    Yields:
        int:
            Omit the type parentheses.

    Unknown:
        Add a section that is not configured.
    """


def out_of_order_and_mutually_exclusive() -> None:
    """
    Params:

    !!! note "Summary"
        Put the sections in the wrong order.

    Returns:
        (int):
            Return a value.

    Yields:
        (int):
            Yield a value.
    """


def non_admonition_as_admonition(value: int) -> None:
    """
    !!! note "Summary"
        Use an admonition for a non-admonition section.

    ??? question "Params"
        value (int):
            Put Params in the wrong format.
    """


def malformed_list_entries(value: int) -> None:
    """
    !!! note "Summary"
        Include malformed parameter and exception entries.

    Params:
        value (int):
            This first entry is well-formed.
        another int:
            This entry has no parenthesised type.

    Raises:
        (ValueError):
            This first entry is well-formed.
        TypeError:
            This entry has no parenthesised type.
    """
    raise ValueError(value)
