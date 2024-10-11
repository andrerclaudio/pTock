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
        tiles_per_pixel_width: int = 1,
        tiles_per_pixel_height: int = 1,
    ) -> None:
        """ """

        initial_column = 0
        initial_line = 0
        last_column = top_left_x
        column = 0
        line = 0

        for slice in symbols:
            element: list = slice

            initial_line = top_left_y

            for height in range(SHAPE_HEIGHT):

                initial_column = last_column

                for width in range(SHAPE_WIDTH):

                    pixel = element.pop(0)

                    line = 0

                    for tile_line in range(tiles_per_pixel_height):

                        line += 1
                        column = 0

                        for tile_column in range(tiles_per_pixel_width):

                            column += 1

                            self.__draw_pixel(
                                color=pixel_color,
                                pixel=pixel,
                                x=(tile_column + initial_column),
                                y=(tile_line + initial_line),
                            )

                    initial_column += column
                initial_line += line
            last_column = initial_column + 1

        self.stdscr.refresh()

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
