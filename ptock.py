#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import curses
from enum import Enum
from datetime import datetime
import threading
from time import sleep


# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

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


class ScreenConnector:
    """Class to manage screen operations using curses."""

    def __init__(self, color: PixelColor = PixelColor.GREEN) -> None:
        self.stdscr: curses.window = None
        self.color = color.value  # Store the integer value of the color enum

    def draw_pixel(self, x: int = 0, y: int = 0) -> None:
        """Draw a pixel at the specified (x, y) coordinates."""
        color_pair = curses.color_pair(self.color)
        self.stdscr.addch(y, x, "█", color_pair)

    def colors_init(self) -> None:
        """Initialize the color system for use in the terminal."""
        curses.initscr()  # Initialize the curses mode
        curses.start_color()  # Enable color functionality

        # Initialize color pairs
        for color in PixelColor:
            curses.init_pair(
                color.value, getattr(curses, f"COLOR_{color.name}"), curses.COLOR_BLACK
            )

    def mount_screen(self) -> None:
        """Draw a pixel and refresh the screen."""
        self.draw_pixel(0, 0)
        self.stdscr.refresh()

    def update(self, timestamp: int) -> None:
        """Update screen by drawing a pixel without clearing previous content."""
        self.mount_screen()

    def application(self, stdscr: curses.window) -> None:
        """Main application logic."""
        self.stdscr = stdscr
        self.colors_init()
        curses.curs_set(0)
        self.mount_screen()
        self.clock = Engine(self.update)
        self.stdscr.getch()
        self.stdscr.clear()
        self.clock.stop()

    def run(self) -> None:
        """Run the curses application."""
        try:
            curses.wrapper(self.application)
        except curses.error as e:
            logger.error(f"Curses error occurred: {e}")
            sys.exit(1)


class Engine(threading.Thread):
    """ """

    def __init__(self, update: ScreenConnector.update) -> None:

        super().__init__(name="Clock beat", daemon=True)

        self.update = update
        self.__stop_event = threading.Event()
        self.start()

    def run(self) -> None:
        """ """

        try:
            # Initialize the thread fetching timestamps from the system clock
            while not self.__stop_event.is_set():

                now = datetime.now()
                timestamp = int(now.timestamp())
                self.update(timestamp)
                sleep(1)

            logger.info("Screen update thread stopped.")

        except threading.ThreadError as e:
            logging.error(f"An error occurred during the thread operation: {e}")
            sys.exit(1)

    def stop(self) -> None:
        """ """
        self.__stop_event.set()


def ptock() -> None:
    """ """
    screen = ScreenConnector()
    screen.run()


if __name__ == "__main__":
    ptock()
