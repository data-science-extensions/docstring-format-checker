def calculate_area(width: int, height: int) -> int:
    """
    Calculate the area of a rectangle.

    Args:
        width (int): The width of the rectangle.
        height (int): The height of the rectangle.

    Returns:
        (int): The calculated area.
    """
    return width * height


def calculate_perimeter(width: int, height: int) -> int:
    """
    Calculate the perimeter of a rectangle.

    Parameters:
        width (int): The width of the rectangle.
        height (int): The height of the rectangle.

    Returns:
        (int): The calculated perimeter.
    """
    return 2 * (width + height)
