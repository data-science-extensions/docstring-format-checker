def calculate_area(width: int, height: int) -> int:
    """
    !!! note "Summary"
        Calculate the area of a rectangle.

    Params:
        width (int): The width of the rectangle.
        height (int): The height of the rectangle.

    Returns:
        (int): The calculated area.
    """
    return width * height


def calculate_perimeter(width: int, height: int) -> int:
    """
    !!! note "Summary"
        Calculate the perimeter of a rectangle.

    Params:
        width (int): The width of the rectangle.
        height (int): The height of the rectangle.

    Returns:
        (int): The calculated perimeter.
    """
    return 2 * (width + height)
