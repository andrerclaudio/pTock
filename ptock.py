#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Built-in libraries
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
        self.x = 0

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
        """Draw the initial pixel and refresh the screen."""
        self.draw_pixel(self.x, self.x)
        self.x += 1
        self.stdscr.refresh()  # Update the screen after all drawing operations

    def update(self, timestamp: int) -> None:
        """ """
        # Call the mount_screen method to handle pixel drawing without clearing the screen
        self.mount_screen()

    def application(self, stdscr: curses.window) -> None:
        """Main application logic."""
        self.stdscr = stdscr  # Update stdscr attribute for use in other methods
        self.colors_init()  # Initialize colors for curses
        curses.curs_set(0)  # Hide the cursor for better visual presentation
        self.mount_screen()  # Mount the screen and draw the pixel
        self.clock = Engine(self.update)  # Start the clock to beat
        self.stdscr.getch()  # Wait for user input to exit
        self.clock.unlock()  # Unlock the thread
        self.stdscr.clear()  # Clear the screen to remove artifacts

    def run(self) -> None:
        """Run the curses application."""
        curses.wrapper(self.application)  # Start the application with curses wrapper


class Engine(threading.Thread):
    """ """

    def __init__(self, update: ScreenConnector.update) -> None:
        """ """
        super().__init__(name="Beating heart")

        # The update object that will be used to update the screen
        self.update = update
        # Control flag for the Clock loop
        self.__lock: bool = True
        # Start the thread immediately after initialization
        self.start()

    def run(self) -> None:
        """ """
        try:

            while self.__lock:
                # Get the current date and time
                now = datetime.now()
                # Convert to timestamp
                timestamp = int(now.timestamp())
                self.update(timestamp)
                sleep(1)

            logging.info("Stopped the clock.")

        except threading.ThreadError as e:
            logging.error(f"An error occurred during the thread operation: {e}")
            sys.exit(1)

    def unlock(self) -> None:
        """
        Stop the loop by setting the __lock attribute to False.
        """
        self.__lock = False


def ptock() -> None:
    """Entry point of the application."""
    screen = ScreenConnector()
    screen.run()


if __name__ == "__main__":
    ptock()
