# Buit-in libraries
#
import logging
import curses
from enum import Enum
from zoneinfo import ZoneInfo
import sys
from datetime import datetime
from font import DIGIT, COLON, H, W

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

    def __init__(
        self, tz: ZoneInfo = None, color: PixelColor = PixelColor.BLUE
    ) -> None:
        self.clock = None
        self.stdscr: curses.window = None
        self.tz_info = tz
        self.last_mapped: list = map_to_symbols([0, 0, ":", 0, 0, ":", 0, 0])
        self.color = color.value  # Store the integer value of the color enum

    def __draw_pixel(self, pixel: str, x: int = 0, y: int = 0) -> None:
        """Draw a pixel at the specified (x, y) coordinates."""
        color_pair = curses.color_pair(self.color)
        try:
            if pixel == "1":
                self.stdscr.addch(y, x, "█", color_pair)
            else:
                self.stdscr.addch(y, x, " ", color_pair)
        except curses.error as e:
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

    def __interpolate(self, n_mapped: list) -> None:
        """ """

        block = 0
        for slice in n_mapped:
            element: list = slice
            element.pop(0)
            for height in range(H):
                for weight in range(W):
                    x = (block * 4) + weight
                    self.__draw_pixel(pixel=element.pop(0), x=x, y=height)
            block += 1
        self.stdscr.refresh()

    def __application(self, stdscr: curses.window) -> None:
        """Main application logic."""
        self.stdscr = stdscr
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
        self.__interpolate(time_mapped)

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
