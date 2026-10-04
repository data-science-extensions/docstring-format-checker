"""Examples of valid docstrings for the post-deployment DFC smoke test."""

# ## Python StdLib Imports ----
from collections.abc import Iterator


def greet(name: str) -> str:
    """
    !!! note "Summary"
        Return a greeting for a person's name.

    ???+ abstract "Details"
        Demonstrate a short summary and an optional details section.

    Params:
        name (str):
            Name to include in the greeting.

    Returns:
        (str):
            A greeting containing the supplied name.

    ???+ example "Examples"
        >>> greet("Ada")
        'Hello, Ada!'

    ??? note "Notes"
        This example uses admonition-style summary and details sections.

    ??? equation "Calculation"
        Combine a greeting prefix with the supplied name.

    ??? question "References"
        No external references are required for this example.
    """
    return f"Hello, {name}!"


async def fetch_record(record_id: int, timeout: float = 5.0) -> str:
    """
    !!! note "Summary"
        Fetch a record using a timeout.

    Params:
        record_id (int):
            Identifier of the record to fetch.
        timeout (float, optional):
            Maximum number of seconds to wait.

    Raises:
        (TimeoutError):
            If the record cannot be fetched before the timeout.

    Returns:
        (str):
            The fetched record.
    """
    return f"record-{record_id}-within-{timeout}"


def count_up(stop: int) -> Iterator[int]:
    """
    !!! note "Summary"
        Generate integers up to the given limit.

    Params:
        stop (int):
            First integer not included in the generated values.

    Raises:
        (ValueError):
            If the requested limit is negative.

    Yields:
        (int):
            The next integer in the sequence.

    ???+ example "Examples"
        >>> list(count_up(3))
        [0, 1, 2]
    """
    yield from range(stop)


class Greeter:
    """
    !!! note "Summary"
        Demonstrate valid class and method docstrings.
    """

    def __init__(self, name: str) -> None:
        """
        !!! note "Summary"
            Store the name used by this greeter.

        Params:
            name (str):
                Name to store.
        """
        self.name = name

    def greet(self, punctuation: str = "!") -> str:
        """
        !!! note "Summary"
            Return a greeting from this instance.

        Params:
            punctuation (str, optional):
                Punctuation to append to the greeting.

        Returns:
            (str):
                A greeting for the stored name.
        """
        return f"Hello, {self.name}{punctuation}"

    @classmethod
    def from_default(cls) -> "Greeter":
        """
        !!! note "Summary"
            Construct a greeter with a default name.

        Returns:
            (Greeter):
                A greeter for the default name.
        """
        return cls("World")

    @staticmethod
    def combine(first: str, second: str) -> str:
        """
        !!! note "Summary"
            Combine two strings with a separator.

        Params:
            first (str):
                First string to combine.
            second (str):
                Second string to combine.

        Returns:
            (str):
                Both strings separated by a space.
        """
        return f"{first} {second}"

    @property
    def name(self) -> str:
        """
        !!! note "Summary"
            Return the stored name.

        Returns:
            (str):
                The name stored by this instance.
        """
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """
        !!! note "Summary"
            Set the stored name.

        Params:
            value (str):
                Name to store.
        """
        self._name = value

    def _private_helper(self, value: int) -> int:
        """
        !!! note "Summary"
            Demonstrate that private methods are checked.

        Params:
            value (int):
                Value to return unchanged.

        Returns:
            (int):
                The supplied value.
        """
        return value
