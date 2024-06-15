from typing import Dict, List, Union

import cv2
import numpy as np


class Color:
    predefined_colors: Dict[str, "Color"] = {}

    def __init__(self, lower: List[int], upper: List[int] = None):
        """
        Defines a color or range of colors. This class converts RGB colors to BGR to satisfy OpenCV's color format.
        Args:
            lower: The lower bound of the color range [R, G, B].
            upper: The upper bound of the color range [R, G, B]. Exclude this arg if you're defining a solid color.
        """
        self.lower = np.array(lower[::-1])
        self.upper = np.array(upper[::-1]) if upper else np.array(lower[::-1])

    def to_hex(self) -> str:
        """Converts the color to a hex string."""
        return "#{:02x}{:02x}{:02x}".format(*self.lower[::-1])

    def to_rgb(self) -> List[int]:
        """Returns the color in RGB format."""
        return self.lower[::-1].tolist()

    def to_bgr(self) -> List[int]:
        """Returns the color in BGR format (OpenCV default)."""
        return self.lower.tolist()

    @classmethod
    def add_predefined_color(cls, name: str, lower: List[int], upper: List[int] = None):
        """
        Adds a new predefined color.
        Args:
            name: The name of the color.
            lower: The lower bound of the color range [R, G, B].
            upper: The upper bound of the color range [R, G, B]. Exclude this arg if you're defining a solid color.
        """
        color = cls(lower, upper)
        cls.predefined_colors[name.upper()] = color
        setattr(cls, name.upper(), color)

    @classmethod
    def get_predefined_color(cls, name: str) -> "Color":
        """
        Retrieves a predefined color by name.
        Args:
            name: The name of the color.
        Returns:
            The Color object associated with the name.
        """
        return cls.predefined_colors.get(name.upper())

    @classmethod
    def list_predefined_colors(cls) -> List[str]:
        """
        Lists all predefined color names.
        Returns:
            A list of predefined color names.
        """
        return list(cls.predefined_colors.keys())


def isolate_colors(image: np.ndarray, colors: Union[Color, List[Color]]) -> np.ndarray:
    """
    Isolates ranges of colors within an image and saves a new resulting image.
    Args:
        image: The image to process.
        colors: A Color or list of Colors.
    Returns:
        The image with the isolated colors (all shown as white).
    """
    if not isinstance(colors, list):
        colors = [colors]
    # Generate masks for each color
    masks = [cv2.inRange(image, color.lower, color.upper) for color in colors]
    # Create black mask
    h, w = image.shape[:2]
    mask = np.zeros([h, w, 1], dtype=np.uint8)
    # Combine masks
    for mask_ in masks:
        mask = cv2.bitwise_or(mask, mask_)
    return mask


"""Solid colors"""
BLACK = Color([0, 0, 0])
BLUE = Color([0, 0, 255])
CYAN = Color([0, 255, 255])
GREEN = Color([0, 255, 0])
ORANGE = Color([255, 144, 64])
PINK = Color([255, 0, 231])
PURPLE = Color([170, 0, 255])
RED = Color([255, 0, 0])
WHITE = Color([255, 255, 255])
YELLOW = Color([255, 255, 0])

"""Colors for use with semi-transparent text"""
OFF_CYAN = Color([0, 200, 200], [70, 255, 255])
OFF_GREEN = Color([0, 100, 0], [30, 255, 255])
OFF_ORANGE = Color([180, 100, 30], [255, 166, 103])
OFF_WHITE = Color([190, 190, 190], [255, 255, 255])
OFF_YELLOW = Color([190, 190, 0], [255, 255, 120])

"""Colors for use with minimap orb text"""
ORB_GREEN = Color([0, 255, 0], [255, 255, 0])
ORB_RED = Color([255, 0, 0], [255, 255, 0])
