# Buit-in libraries
#
import curses
from enum import Enum
from zoneinfo import ZoneInfo
import sys
from datetime import datetime

# Custom-made libraries
#
from mechanism import Quartz
from font import (
    DIGIT,
    COLON,
    SHAPE_HEIGHT,
    SHAPE_WIDTH,
    SPACE,
    LETTER_A,
    LETTER_M,
    LETTER_P,
)


class PixelColor(Enum):
    """Enumeration of pixel colors."""

    BLACK = 8
    BLUE = 4
    CYAN = 6
    GREEN = 2
    MAGENTA = 5
    RED = 1
    WHITE = 7
    YELLOW = 3


class ViewConnector:
    """Class to manage screen operations using curses."""

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 2,
        height: int = 1,
        second: bool = False,
        military: bool = False,
        center: bool = False,
        color: int = 2,
        timezone: ZoneInfo = None,
    ) -> None:
        self.top_left_x = x
        self.top_left_y = y
        self.tiles_per_pixel_width = width
        self.tiles_per_pixel_height = height
        self.show_seconds = second
        self.military_time = military
        self.align_to_center = center
        self.pixel_color = (
            color
            if PixelColor.RED.value <= color <= PixelColor.BLACK.value
            else PixelColor.GREEN.value
        )
        self.tz_info: ZoneInfo = timezone
        self.stdscr: curses.window = None
        self.screen_height: int = 0
        self.screen_width: int = 0
        self.pixel_buffer: dict = {}

    def __draw_pixel(self, pixel: str, x: int = 0, y: int = 0) -> None:
        """Draw a pixel at the specified (x, y) coordinates."""
        color_pair = curses.color_pair(self.pixel_color)
        key = f"{x}:{y}"

        # Check if the pixel is already in the buffer and if it's the same
        if key not in self.pixel_buffer or self.pixel_buffer[key] != pixel:
            self.pixel_buffer[key] = pixel  # Save the pixel in the buffer
            try:
                # Use '█' for pixel '1' and space for '0'
                self.stdscr.addch(y, x, "█" if pixel == "1" else " ", color_pair)
            except curses.error as e:
                # Remove the pixel from buffer if drawing fails
                self.pixel_buffer.pop(key, None)

    @staticmethod
    def __colors_init() -> None:
        """Initialize the color system for use in the terminal."""
        curses.initscr()  # Initialize the curses mode
        curses.start_color()  # Enable color functionality
        curses.use_default_colors()

        # Initialize color pairs
        for color in PixelColor:
            curses.init_pair(color.value, getattr(curses, f"COLOR_{color.name}"), -1)

    def __interpolate(
        self,
        symbols: list,
    ) -> None:
        """Interpolates a grid of symbols into pixels on a display.

        Args:
            symbols (list): A list of symbol slices to be drawn.
        """

        # Initialize starting position for drawing
        last_column_position = self.top_left_x

        # Iterate through each symbol slice
        for symbol_slice in symbols:
            current_line_position = (
                self.top_left_y
            )  # Reset vertical position for each slice

            # Iterate over the height of the symbol
            for row in range(SHAPE_HEIGHT):
                column_position = (
                    last_column_position  # Start from the left for each row
                )

                # Iterate over the width of the symbol
                for col in range(SHAPE_WIDTH):
                    pixel_value = symbol_slice.pop(0)  # Get the next pixel value

                    # Draw tiles for this pixel
                    for tile_row in range(self.tiles_per_pixel_height):
                        for tile_col in range(self.tiles_per_pixel_width):
                            self.__draw_pixel(
                                pixel=pixel_value,
                                x=(column_position + tile_col),  # Calculate x position
                                y=(
                                    current_line_position + tile_row
                                ),  # Calculate y position
                            )

                    column_position += self.tiles_per_pixel_width  # Move to next column

                current_line_position += self.tiles_per_pixel_height  # Move to next row

            last_column_position += (
                SHAPE_WIDTH * self.tiles_per_pixel_width
                + self.tiles_per_pixel_width  # Move to next slice
            )

        self.stdscr.refresh()  # Refresh display to show changes

    def __calculate_center_xy_position(self) -> None:
        """ """

        clock_digits_count = (
            #
            5
            + (3 if self.show_seconds else 0)
            + (3 if not self.military_time else 0)
        )

        # Calculate dimensions for centering
        pixel_height = SHAPE_HEIGHT * self.tiles_per_pixel_height
        pixel_width = SHAPE_WIDTH * self.tiles_per_pixel_width

        total_length_with_spaces = (
            clock_digits_count * pixel_width
            + (clock_digits_count - 1) * self.tiles_per_pixel_width
        )

        # Centering calculations
        self.top_left_y = round((self.screen_height - pixel_height) / 2)
        self.top_left_x = round((self.screen_width - total_length_with_spaces) / 2)

    def __check_fit(self) -> bool:
        """Check if the clock can fit within the available screen space and given passed parameters."""

        pixel_height = SHAPE_HEIGHT * self.tiles_per_pixel_height

        if (self.screen_height - self.top_left_y) < pixel_height:
            return False

        clock_digits_count = (
            #
            5
            + (3 if self.show_seconds else 0)
            + (3 if not self.military_time else 0)
        )

        pixel_width = SHAPE_WIDTH * self.tiles_per_pixel_width

        total_length_with_spaces = (
            clock_digits_count * pixel_width
            + (clock_digits_count - 1) * self.tiles_per_pixel_width
        )

        return (
            True
            if (self.screen_width - self.top_left_x) >= total_length_with_spaces
            else False
        )

    def __application(self, stdscr: curses.window) -> None:
        """Main application logic."""
        self.stdscr = stdscr
        self.screen_height, self.screen_width = self.stdscr.getmaxyx()

        if self.align_to_center:
            self.__calculate_center_xy_position()

        if not self.__check_fit():
            sys.exit(1)

        self.__colors_init()
        curses.curs_set(0)
        self.clock = Quartz(self.update, tz=self.tz_info)

        self.stdscr.getch()
        self.stdscr.clear()
        self.clock.stop()

    def update(self, current_time: datetime) -> None:
        """Update screen by drawing a pixel without clearing previous content."""

        time_components: list = datetime_slicer(
            now=current_time,
            show_seconds=self.show_seconds,
            military_time=self.military_time,
        )
        symbol_mappings: list = map_to_symbols(time_components)
        self.__interpolate(symbols=symbol_mappings)

    def run(self) -> None:
        """Run the curses application."""

        try:
            curses.wrapper(self.__application)

        except curses.error as e:
            sys.exit(1)


def datetime_slicer(
    now: datetime, show_seconds: bool = False, military_time: bool = False
) -> list[int]:
    """Slice the current datetime into its individual components.

    This function takes a datetime object and extracts the hour, minute,
    and second components along with AM/PM designation if required. It
    returns a list containing each component as an integer, formatted with
    colons, and may include AM/PM if not using military time.

    Args:
        now (datetime): The current datetime to be sliced.
        show_seconds (bool): Flag indicating whether to include seconds in output. Defaults to False.
        military_time (bool): Flag indicating whether to use military time (24-hour format). Defaults to False.

    Returns:
        list[int]: A list containing the tens and units of hours, minutes,
                    and seconds, interspersed with string colons.
                    Example: [hour_tens, hour_units, ":", minute_tens,
                    minute_units, ":", second_tens, second_units]
    """

    # Determine hour format based on military_time flag
    hours = now.hour if military_time else int(now.strftime("%I"))  # 12-hour format
    am_pm = "" if military_time else now.strftime("%p")  # AM/PM designator

    minutes = int(now.strftime("%M"))
    seconds = int(now.strftime("%S")) if show_seconds else None

    # Prepare the output list
    output = [
        hours // 10,  # Tens place of hours
        hours % 10,  # Units place of hours
        ":",  # Separator for time components
        minutes // 10,  # Tens place of minutes
        minutes % 10,  # Units place of minutes
    ]

    # Include seconds and AM/PM if necessary
    if show_seconds:
        output.extend(
            [
                ":",  # Separator for seconds
                seconds // 10,  # Tens place of seconds
                seconds % 10,  # Units place of seconds
            ]
        )

    if not military_time:
        output.append(" ")  # Space before AM/PM indicator
        output.extend(list(am_pm))  # Add AM/PM indicator

    return output


def map_to_symbols(elements: list[int | str]) -> list[list[str]]:
    """Map time slices to their corresponding binary string representations.

    This function takes a list of time components (digits and colons)
    and converts each component into its binary string representation
    using predefined mappings. The output is a pixel buffer where each
    element is represented as a list of strings.

    Args:
        elements (list[int | str]): A list containing integers (0-9)
                                     representing digits and strings
                                     for colons, spaces, AM, and PM.

    Returns:
        list[list[str]]: A nested list where each inner list represents
                          the binary string of a corresponding time component.
    """

    pixel_buffer = []
    for element in elements:
        if isinstance(element, str):
            pixel_buffer.append(
                list(
                    {
                        ":": COLON,
                        " ": SPACE,
                        "A": LETTER_A,
                        "P": LETTER_P,
                        "M": LETTER_M,
                    }[element]
                )
            )
        else:
            pixel_buffer.append(list(DIGIT[element]))

    return pixel_buffer
