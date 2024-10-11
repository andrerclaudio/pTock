# Buit-in libraries
#
import logging
import curses
from enum import Enum
from zoneinfo import ZoneInfo
import sys
from datetime import datetime
from font import DIGIT, COLON, SHAPE_HEIGHT, SHAPE_WIDTH, SPACE

# Custom-made libraries
#
from mechanism import Quartz

logger = logging.getLogger(__name__)


class PixelColor(Enum):
    """Enumeration of pixel colors."""

    BLACK = 1
    BLUE = 2
    CYAN = 3
    GREEN = 4
    MAGENTA = 5
    RED = 6
    WHITE = 7
    YELLOW = 8


class ViewConnector:
    """Class to manage screen operations using curses."""

    def __init__(self, timezone: ZoneInfo = None) -> None:
        self.clock = None
        self.stdscr: curses.window = None
        self.max_height: int = 0
        self.max_width: int = 0
        self.tz_info: ZoneInfo = timezone
        self.pixel_buffer: dict = {}

    def __draw_pixel(
        self, color: PixelColor, pixel: str, x: int = 0, y: int = 0
    ) -> None:
        """Draw a pixel at the specified (x, y) coordinates."""
        color_pair = curses.color_pair(color)
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
        pixel_color: PixelColor = PixelColor.GREEN.value,
        align_to_center: bool = False,
        top_left_x: int = 0,
        top_left_y: int = 0,
        tiles_per_pixel_width: int = 2,
        tiles_per_pixel_height: int = 1,
    ) -> None:
        """Interpolates a grid of symbols into pixels on a display.

        Args:
            symbols (list): A list of symbol slices to be drawn.
            pixel_color (PixelColor): The color used for drawing pixels.
            align_to_center (bool): If True, aligns the symbols to the center.
            top_left_x (int): The x-coordinate of the top-left corner for drawing.
            top_left_y (int): The y-coordinate of the top-left corner for drawing.
            tiles_per_pixel_width (int): Number of tiles per pixel in width.
            tiles_per_pixel_height (int): Number of tiles per pixel in height.
        """

        if align_to_center:
            # Calculate dimensions for centering
            pixel_height = SHAPE_HEIGHT * tiles_per_pixel_height
            pixel_width = SHAPE_WIDTH * tiles_per_pixel_width

            total_length_with_spaces = (
                len(symbols) * pixel_width + (len(symbols) - 1) * tiles_per_pixel_width
            )

            # Centering calculations
            top_left_y = round((self.max_height - pixel_height) / 2)
            top_left_x = round((self.max_width - total_length_with_spaces) / 2)

        # Initialize starting position for drawing
        last_column_position = top_left_x

        # Iterate through each symbol slice
        for symbol_slice in symbols:
            current_line_position = top_left_y  # Reset vertical position for each slice

            # Iterate over the height of the symbol
            for row in range(SHAPE_HEIGHT):
                column_position = (
                    last_column_position  # Start from the left for each row
                )

                # Iterate over the width of the symbol
                for col in range(SHAPE_WIDTH):
                    pixel_value = symbol_slice.pop(0)  # Get the next pixel value

                    # Draw tiles for this pixel
                    for tile_row in range(tiles_per_pixel_height):
                        for tile_col in range(tiles_per_pixel_width):
                            self.__draw_pixel(
                                color=pixel_color,
                                pixel=pixel_value,
                                x=column_position + tile_col,  # Calculate x position
                                y=current_line_position
                                + tile_row,  # Calculate y position
                            )

                    column_position += tiles_per_pixel_width  # Move to next column

                current_line_position += tiles_per_pixel_height  # Move to next row

            last_column_position += (
                SHAPE_WIDTH * tiles_per_pixel_width
                + tiles_per_pixel_width  # Move to next slice
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

    def update(self, now: datetime) -> None:
        """Update screen by drawing a pixel without clearing previous content."""

        time_slices: list = datetime_slicer(now)
        time_mapped: list = map_to_symbols(time_slices)
        self.__interpolate(symbols=time_mapped)

    def run(self) -> None:
        """Run the curses application."""

        try:
            curses.wrapper(self.__application)

        except curses.error as e:
            logger.error(f"Curses error occurred: {e}")
            sys.exit(1)


def datetime_slicer(now: datetime) -> list:
    """ """
    seconds = now.second
    minutes = now.minute
    hours = now.hour

    hour_dec, hour_unit = divmod(hours, 10)
    min_dec, min_unit = divmod(minutes, 10)
    sec_dec, sec_unit = divmod(seconds, 10)

    return [hour_dec, hour_unit, ":", min_dec, min_unit, ":", sec_dec, sec_unit]


def map_to_symbols(elements: list) -> list:
    """ """
    pixel_buffer = []

    number = DIGIT[elements[0]]
    binary_str = list(number)
    pixel_buffer.append(binary_str)

    number = DIGIT[elements[1]]
    binary_str = list(number)
    pixel_buffer.append(binary_str)

    number = COLON
    binary_str = list(number)
    pixel_buffer.append(binary_str)

    number = DIGIT[elements[3]]
    binary_str = list(number)
    pixel_buffer.append(binary_str)

    number = DIGIT[elements[4]]
    binary_str = list(number)
    pixel_buffer.append(binary_str)

    number = COLON
    binary_str = list(number)
    pixel_buffer.append(binary_str)

    number = DIGIT[elements[6]]
    binary_str = list(number)
    pixel_buffer.append(binary_str)

    number = DIGIT[elements[7]]
    binary_str = list(number)
    pixel_buffer.append(binary_str)

    return pixel_buffer
