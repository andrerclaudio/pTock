#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import curses
from enum import Enum
from datetime import datetime
import threading
from time import sleep
import sys


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
    """Engine class responsible for periodically updating the screen with a timestamp.

    This class runs in a separate thread, fetching the current system timestamp
    every second. It invokes the provided `update` method to refresh the screen
    with the new timestamp until stopped.
    """

    def __init__(self, update: ScreenConnector.update) -> None:
        """Initialize the Engine thread.

        Args:
            update (ScreenConnector.update): A function that will be called with the current
            Unix timestamp each second to update the screen.
        """
        super().__init__(name="Clock beat", daemon=True)
        self.update = update  # Function to update the screen with the timestamp
        self.__stop_event = threading.Event()  # Event to signal thread termination
        self.start()  # Start the thread immediately after initialization

    def run(self) -> None:
        """Main loop of the Engine thread.

        Continuously fetches the current system timestamp and calls the `update`
        function with it every second. The loop continues until the stop event is set.
        Logs a message when the thread terminates.

        Raises:
            Exception: Catches and logs any exception that occurs during execution,
            terminating the program if an error arises.
        """
        try:
            while not self.__stop_event.is_set():
                now = datetime.now()  # Get the current date and time
                timestamp = int(now.timestamp())  # Convert the time to a Unix timestamp
                self.update(timestamp)  # Call the update function with the timestamp
                sleep(1)  # Pause for one second before the next update

            logger.info("Screen update thread stopped.")

        except Exception as e:  # Catch all exceptions
            logging.error(f"An error occurred during thread execution: {e}")
            sys.exit(1)  # Exit the program in case of an error

    def stop(self) -> None:
        """Stop the Engine thread.

        Sets the stop event, signaling the thread to exit the main loop and terminate gracefully.
        """
        self.__stop_event.set()  # Signal the thread to stop


def ptock() -> None:
    """ """
    screen = ScreenConnector()
    screen.run()


if __name__ == "__main__":
    ptock()
