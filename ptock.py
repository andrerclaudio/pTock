#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Buit-in libraries
#
import logging
import argparse
from zoneinfo import ZoneInfo

# Custom-made libraries
#
from view import ViewConnector

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def ptock(x, y, width, height, second, military, center, color, format) -> None:
    """Starts the digital clock with specified settings."""
    tz = ZoneInfo("America/Argentina/Buenos_Aires")  # Set to Buenos Aires, Argentina.
    # clock = ViewConnector(timezone=tz)

    # Here you can use the parameters (x, y, width, height, etc.) as needed
    print(
        f"Clock settings: Position({x}, {y}), Width: {width}, Height: {height}, "
        f"Display Seconds: {second}, Military Time: {military}, Centered: {center}, "
        f"Color: {color}, Date Format: '{format}'"
    )

    # clock.run()


class CustomHelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog):
        """Initialize the custom help formatter with a wider max_help_position."""
        super().__init__(prog, max_help_position=36)

    def _format_action_invocation(self, action):
        """Format the invocation of an action (argument)."""
        if not action.option_strings:
            # Default formatting for positional arguments
            return super()._format_action_invocation(action)

        # Customize for optional arguments
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


if __name__ == "__main__":
    """
    Entry point for the script when run as the main module.

    Parses the command-line arguments for the horizontal and vertical position,
    font dimensions, display settings, and then calls the ptock function to start the
    application.
    """

    parser = argparse.ArgumentParser(
        description="A digital clock for the terminal.",
        usage="tock [OPTIONS]",
        formatter_class=CustomHelpFormatter,
    )

    # Add command-line arguments
    parser.add_argument(
        "-x",
        "--x",
        type=int,
        default=0,
        help="Horizontal 0-indexed position of top-left corner [default: 0]",
    )
    parser.add_argument(
        "-y",
        "--y",
        type=int,
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
        type=int,
        default=2,
        help="Change the color of the time [default: 2]",
    )
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        default="%F | %Z",
        help='Change the date format [default: "%%F | %%Z"]',
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    # Start the main application with the parsed arguments
    ptock(
        args.x,
        args.y,
        args.width,
        args.height,
        args.second,
        args.military,
        args.center,
        args.color,
        args.format,
    )
