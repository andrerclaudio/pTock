#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Built-in libraries
import logging
import curses
from enum import Enum


class Color(Enum):
    """
    Enumeration for color constants.
    """
    BLUE = 1
    RED = 2
    YELLOW = 3
    GREEN = 4


# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


def draw_pixels(stdscr):
    """
    """
    
    # Initialize the color system for use in the terminal
    curses.start_color()

    # Define a color pair: GREEN text on BLACK background
    curses.init_pair(Color.GREEN.value, curses.COLOR_GREEN, curses.COLOR_BLACK)

    # Hide the cursor for better visual presentation
    curses.curs_set(0)

    # Draw two rows of colored pixels
    for y in range(10):  # Loop through two rows (0 and 1)
        for x in range(10):  # Loop through ten columns (0 to 9)
            color_pair = curses.color_pair(Color.GREEN.value)
            stdscr.addch(y, x, "█", color_pair)  # Draw a character at (y, x) with specified color
        
        
    stdscr.refresh()  # Update the screen once after all drawing operations
    stdscr.getch()  # Wait for user input to exit

    # Clear the screen before exiting (optional)
    stdscr.clear()


if __name__ == "__main__":
    """
    """
    
    # Use ncurses wrapper to handle initialization and cleanup automatically
    curses.wrapper(draw_pixels)
