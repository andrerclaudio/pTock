#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Built-in libraries
import logging
import curses
from enum import Enum


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
        self.color: int = color.value  # Store the integer value of the color enum

    def colors_init(self) -> None:
        """Initialize the color system for use in the terminal."""
        curses.initscr()
        curses.start_color()

        # Initialize color pairs
        for color in PixelColor:
            curses.init_pair(
                color.value, getattr(curses, f"COLOR_{color.name}"), curses.COLOR_BLACK
            )

    def draw_pixel(self, x: int = 0, y: int = 0) -> None:
        """Draw a pixel at the specified (x, y) coordinates."""
        color_pair = curses.color_pair(self.color)
        self.stdscr.addch(y, x, "█", color_pair)

    def mount_screen(self) -> None:
        """Mount the screen and draw initial graphics."""
        self.draw_pixel(0, 0)  # Draw the pixel at (0, 0)
        self.stdscr.refresh()  # Update the screen after all drawing operations

    def application(self, stdscr: curses.window) -> None:
        """Main application logic."""
        self.stdscr = stdscr  # Update stdscr attribute for use in other methods
        self.colors_init()  # Initialize colors for curses
        curses.curs_set(0)  # Hide the cursor for better visual presentation
        self.mount_screen()  # Mount the screen and draw the pixel
        self.stdscr.getch()  # Wait for user input to exit
        self.stdscr.clear()  # Clear the screen to remove artifacts

    def run(self) -> None:
        """Run the curses application."""
        curses.wrapper(self.application)


def ptock() -> None:
    """Entry point of the application."""
    cursor = ScreenConnector()
    cursor.run()  # Start the application


if __name__ == "__main__":
    ptock()
