# Buit-in libraries
#
import logging
import curses
from enum import Enum
from zoneinfo import ZoneInfo
import sys
from datetime import datetime

# Custom-made libraries
#
from mechanism import Quartz
from font import DIGIT, COLON, SHAPE_HEIGHT, SHAPE_WIDTH

logger = logging.getLogger(__name__)


class PixelColor(Enum):
    """Enumeration of pixel colors."""

    BLACK = 8
    BLUE = 4
    CYAN = 6
    GREEN = 2
    MAGENTA = 5
    RED = 1
    WHITE = 7
    YELLOW = 3


class ViewConnector:
    """Class to manage screen operations using curses."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        second: bool,
        military: bool,
        center: bool,
        color: int,
        timezone: ZoneInfo = None,
    ) -> None:
        self.top_left_x = x
        self.top_left_y = y
        self.tiles_per_pixel_width = width
        self.tiles_per_pixel_height = height
        self.show_seconds = second
        self.military_time = military
        self.align_to_center = center
        self.pixel_color = color
        self.tz_info: ZoneInfo = timezone
        self.stdscr: curses.window = None
        self.max_height: int = 0
        self.max_width: int = 0
        self.pixel_buffer: dict = {}

    def __draw_pixel(self, pixel: str, x: int = 0, y: int = 0) -> None:
        """Draw a pixel at the specified (x, y) coordinates."""
        color_pair = curses.color_pair(self.pixel_color)
        key = f"{x}{y}"

        # Check if the pixel is already in the buffer and if it's the same
        if key not in self.pixel_buffer or self.pixel_buffer[key] != pixel:
            self.pixel_buffer[key] = pixel  # Save the pixel in the buffer
            try:
                # Use '█' for pixel '1' and space for '0'
                self.stdscr.addch(y, x, "█" if pixel == "1" else " ", color_pair)
            except curses.error as e:
                # Remove the pixel from buffer if drawing fails
                self.pixel_buffer.pop(key, None)
                logger.error(f"Error drawing pixel at ({x}, {y}): {e}", exc_info=False)

    @staticmethod
    def __colors_init() -> None:
        """Initialize the color system for use in the terminal."""
        curses.initscr()  # Initialize the curses mode
        curses.start_color()  # Enable color functionality

        # Initialize color pairs
        for color in PixelColor:
            curses.init_pair(
                color.value, getattr(curses, f"COLOR_{color.name}"), curses.COLOR_BLACK
            )

    def __interpolate(
        self,
        symbols: list,
    ) -> None:
        """Interpolates a grid of symbols into pixels on a display.

        Args:
            symbols (list): A list of symbol slices to be drawn.
        """

        if self.align_to_center:
            # Calculate dimensions for centering
            pixel_height = SHAPE_HEIGHT * self.tiles_per_pixel_height
            pixel_width = SHAPE_WIDTH * self.tiles_per_pixel_width

            total_length_with_spaces = (
                len(symbols) * pixel_width
                + (len(symbols) - 1) * self.tiles_per_pixel_width
            )

            # Centering calculations
            self.top_left_y = round((self.max_height - pixel_height) / 2)
            self.top_left_x = round((self.max_width - total_length_with_spaces) / 2)

        # Initialize starting position for drawing
        last_column_position = self.top_left_x

        # Iterate through each symbol slice
        for symbol_slice in symbols:
            current_line_position = (
                self.top_left_y
            )  # Reset vertical position for each slice

            # Iterate over the height of the symbol
            for row in range(SHAPE_HEIGHT):
                column_position = (
                    last_column_position  # Start from the left for each row
                )

                # Iterate over the width of the symbol
                for col in range(SHAPE_WIDTH):
                    pixel_value = symbol_slice.pop(0)  # Get the next pixel value

                    # Draw tiles for this pixel
                    for tile_row in range(self.tiles_per_pixel_height):
                        for tile_col in range(self.tiles_per_pixel_width):
                            self.__draw_pixel(
                                pixel=pixel_value,
                                x=column_position + tile_col,  # Calculate x position
                                y=current_line_position
                                + tile_row,  # Calculate y position
                            )

                    column_position += self.tiles_per_pixel_width  # Move to next column

                current_line_position += self.tiles_per_pixel_height  # Move to next row

            last_column_position += (
                SHAPE_WIDTH * self.tiles_per_pixel_width
                + self.tiles_per_pixel_width  # Move to next slice
            )

        self.stdscr.refresh()  # Refresh display to show changes

    def __application(self, stdscr: curses.window) -> None:
        """Main application logic."""
        self.stdscr = stdscr
        self.max_height, self.max_width = self.stdscr.getmaxyx()
        self.__colors_init()
        curses.curs_set(0)
        self.clock = Quartz(self.update, tz=self.tz_info)

        self.stdscr.getch()
        self.stdscr.clear()
        self.clock.stop()

    def update(self, current_time: datetime) -> None:
        """Update screen by drawing a pixel without clearing previous content."""

        time_components: list = datetime_slicer(
            now=current_time, show_seconds=self.show_seconds
        )
        symbol_mappings: list = map_to_symbols(time_components)
        self.__interpolate(symbols=symbol_mappings)

    def run(self) -> None:
        """Run the curses application."""

        try:
            curses.wrapper(self.__application)

        except curses.error as e:
            logger.error(f"Curses error occurred: {e}")
            sys.exit(1)


def datetime_slicer(now: datetime, show_seconds: bool = False) -> list[int]:
    """Slice the current datetime into its individual components.

    This function takes a datetime object and extracts the hour, minute,
    and second components. It returns a list containing each component
    as an integer, with colons represented as strings for formatting.

    Args:
        now (datetime): The current datetime to be sliced.

    Returns:
        list[int]: A list containing the tens and units of hours, minutes,
                    and seconds, interspersed with string colons.
                    Example: [hour_tens, hour_units, ":", minute_tens,
                              minute_units, ":", second_tens, second_units]
    """
    if show_seconds:

        return [
            now.hour // 10,
            now.hour % 10,
            ":",
            now.minute // 10,
            now.minute % 10,
            ":",
            now.second // 10,
            now.second % 10,
        ]

    else:

        return [
            now.hour // 10,
            now.hour % 10,
            ":",
            now.minute // 10,
            now.minute % 10,
        ]


def map_to_symbols(elements: list[int | str]) -> list[list[str]]:
    """Map time slices to their corresponding binary string representations.

    This function takes a list of time components (digits and colons)
    and converts each component into its binary string representation
    using predefined mappings. The output is a pixel buffer where each
    element is represented as a list of strings.

    Args:
        elements (list[int | str]): A list containing integers (0-9)
                                     representing digits and strings
                                     for colons.

    Returns:
        list[list[str]]: A nested list where each inner list represents
                          the binary string of a corresponding time component.
    """
    pixel_buffer = []

    # Create a mapping for each element to its binary representation
    for element in elements:
        if isinstance(element, str):  # Handle colons directly
            pixel_buffer.append(list(COLON))
        else:
            pixel_buffer.append(list(DIGIT[element]))

    return pixel_buffer
