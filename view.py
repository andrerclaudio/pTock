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
        self, tz: ZoneInfo = None, color: PixelColor = PixelColor.GREEN
    ) -> None:
        self.clock = None
        self.stdscr: curses.window = None
        self.tz_info = tz
        self.color = color.value  # Store the integer value of the color enum

    def __draw_pixel(self, x: int = 0, y: int = 0) -> None:
        """Draw a pixel at the specified (x, y) coordinates."""
        color_pair = curses.color_pair(self.color)
        try:
            self.stdscr.addch(y, x, "█", color_pair)
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

    def __interpolate(self) -> None:
        """Draw a pixel and refresh the screen."""
        self.__draw_pixel(0, 0)
        self.stdscr.refresh()

    def __application(self, stdscr: curses.window) -> None:
        """Main application logic."""
        self.stdscr = stdscr
        self.__colors_init()
        curses.curs_set(0)
        self.__interpolate()
        self.clock = Quartz(self.update, tz=self.tz_info)
        self.stdscr.getch()
        self.stdscr.clear()
        self.clock.stop()

    def update(self, now: datetime) -> None:
        """Update screen by drawing a pixel without clearing previous content."""
        self.__interpolate()

    def run(self) -> None:
        """Run the curses application."""

        try:
            curses.wrapper(self.__application)

        except curses.error as e:
            logger.error(f"Curses error occurred: {e}")
            sys.exit(1)
