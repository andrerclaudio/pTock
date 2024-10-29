#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Built-in libraries
import argparse
import os
import subprocess
from random import randint
from zoneinfo import ZoneInfo

# Custom-made libraries
from .view import ViewConnector


# Non-negative integer validation
def non_negative_int_check(value):
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError(f"{value} must be 0 or a positive integer")
    return ivalue


# Color range validation
def color_range_check(value):
    ivalue = int(value)
    if ivalue < 0 or ivalue > 7:
        raise argparse.ArgumentTypeError(f"{value} must be an integer between 0 and 7")
    return ivalue


def get_system_timezone() -> str:
    """
    Retrieves the system's current timezone using the 'timedatectl' command.

    This function executes the 'timedatectl' command, which provides system time
    information, and parses its output to extract the active timezone. If the timezone
    cannot be determined (e.g., due to a missing command or parsing error), it falls back to UTC.

    Returns:
        str: The system's current timezone as a string (e.g., "America/New_York").
             Returns "UTC" if the timezone cannot be determined.
    """
    try:
        # Run the 'timedatectl' command and capture the output
        result = subprocess.run(["timedatectl"], stdout=subprocess.PIPE, text=True)

        # Iterate over each line of the output
        for line in result.stdout.splitlines():
            # Look for the line that contains 'Time zone'
            if "Time zone" in line:
                # Extract and return the timezone part of the line
                return line.split(":")[1].strip().split(" ")[0]
    except Exception as e:
        # Problem fetching the Timezone information. Continue without it.
        pass

    # Return 'UTC' as a fallback in case of an error
    return "UTC"


def ptock(
    color_code=None,
    x: int = 0,
    y: int = 0,
    width: int = 2,
    height: int = 1,
    show_seconds: bool = False,
    military_time: bool = False,
    center_clock: bool = False,
) -> None:
    """
    Starts a digital clock with specified settings in the terminal.

    This function initializes and runs a digital clock display with customizable
    parameters such as position, size and color. The clock can
    be configured to show seconds and to use either 12-hour or military (24-hour)
    time format.

    Args:
        color_code (int): Color code for displaying the clock. Defaults to a random value from 1 to 7.
        x (int): Horizontal 0-indexed position of the top-left corner of the clock.
        y (int): Vertical 0-indexed position of the top-left corner of the clock.
        width (int): Font width in characters per tile.
        height (int): Font height in characters per tile.
        show_seconds (bool): Flag indicating whether to display seconds. Defaults to False.
        military_time (bool): Flag indicating whether to display military (24-hour) time. Defaults to False.
        center_clock (bool): Flag indicating whether to center the clock in the terminal. Defaults to False.

    Returns:
        None: This function does not return any value; it runs the clock application directly.
    """

    # Ensure TERM is set to xterm-256color for proper color support
    os.environ["TERM"] = "xterm-256color"

    # Get system timezone dynamically
    system_timezone = get_system_timezone()

    # Set the timezone to Buenos Aires, Argentina
    timezone = ZoneInfo(system_timezone)

    # Create an instance of ViewConnector with the provided settings
    clock = ViewConnector(
        x=x,  # Horizontal position
        y=y,  # Vertical position
        width=width,  # Width of the clock tiles
        height=height,  # Height of the clock tiles
        show_seconds=show_seconds,  # Display seconds or not
        military_time=military_time,  # Use 24-hour format or not
        center=center_clock,  # Center the clock or use custom positioning
        color=(
            randint(1, 7) if not color_code else color_code
        ),  # Color setting for the clock
        timezone=timezone,  # Timezone for the clock
    )

    # Run the clock application
    clock.run()


class CustomHelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog):
        """Initialize the custom help formatter with a wider max_help_position."""
        super().__init__(prog, max_help_position=36)

    def _format_action_invocation(self, action):
        """Format the invocation of an action (argument)."""
        if not action.option_strings:
            return super()._format_action_invocation(
                action
            )  # Default formatting for positional arguments

        option_string = ", ".join(action.option_strings)

        if action.nargs != 0:
            metavar = self._format_args(action, action.dest.upper())
            return f"{option_string} <{metavar}>"

        return option_string

    def add_usage(self, usage, actions, groups, prefix=None):
        """Override to ensure 'Usage:' starts with an uppercase letter."""
        if prefix is None:
            prefix = "Usage: "
        return super().add_usage(usage, actions, groups, prefix)

    def start_section(self, heading):
        """Override to ensure 'Options:' is properly capitalized."""
        if heading.lower() == "options":
            heading = "Options"
        return super().start_section(heading)


def main():
    """
    Entry point for the script when run as the main module.

    Parses command-line arguments for horizontal and vertical position,
    font dimensions, display settings, and then calls the ptock function
    to start the application.
    """

    parser = argparse.ArgumentParser(
        description="A digital clock for the terminal.",
        usage="ptock [OPTIONS]",
        formatter_class=CustomHelpFormatter,
    )

    # Add command-line arguments
    parser.add_argument(
        "-x",
        "--x",
        type=non_negative_int_check,
        default=0,
        help="Horizontal 0-indexed position of top-left corner [default: 0]",
    )

    parser.add_argument(
        "-y",
        "--y",
        type=non_negative_int_check,
        default=0,
        help="Vertical 0-indexed position of top-left corner [default: 0]",
    )

    parser.add_argument(
        "-W",
        "--width",
        type=int,
        default=2,
        help="Font width in characters per tile [default: 2]",
    )

    parser.add_argument(
        "-H",
        "--height",
        type=int,
        default=1,
        help="Font height in characters per tile [default: 1]",
    )

    parser.add_argument("-s", "--second", action="store_true", help="Display seconds")

    parser.add_argument(
        "-m", "--military", action="store_true", help="Display military (24-hour) time"
    )

    parser.add_argument(
        "-c",
        "--center",
        action="store_true",
        help="Center the clock in the terminal. Overrides manual positioning",
    )

    parser.add_argument(
        "-C",
        "--color",
        type=color_range_check,
        required=False,
        help="Change the color of the time [not required]. The options are: "
        "1-red, 2-green, 3-yellow, 4-blue, 5-magenta, 6-cyan, 7-white and 0-black",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="ptock: v1.3.1",
        help="Show program's version number and exit",
    )

    # Parse command-line arguments
    args = parser.parse_args()

    # Start the main application with parsed arguments
    ptock(
        args.color,
        x=args.x,
        y=args.y,
        width=args.width,
        height=args.height,
        show_seconds=args.second,
        military_time=args.military,
        center_clock=args.center,
    )
