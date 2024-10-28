# Built-in libraries
import curses
import sys
from datetime import datetime
from enum import Enum
from typing import Optional
from zoneinfo import ZoneInfo

# Custom-made libraries
from .mechanism import Quartz
from .font import (
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
    """Enumeration of pixel colors used in the display."""

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
        show_seconds: bool = False,
        military_time: bool = False,
        center: bool = False,
        color: int = 2,
        timezone: ZoneInfo = None,
    ) -> None:
        """
        Initialize the ViewConnector with display settings.

        Args:
            x (int): Horizontal position of the top-left corner of the clock.
            y (int): Vertical position of the top-left corner of the clock.
            width (int): Width of each digit in characters.
            height (int): Height of each digit in characters.
            show_seconds (bool): Flag to indicate if seconds should be displayed.
            military_time (bool): Flag to indicate if military time format should be used.
            center (bool): Flag to indicate if the clock should be centered.
            color (int): Color code for pixel color.
            timezone (ZoneInfo): Timezone for the clock display.
        """

        self.top_left_x = x
        self.top_left_y = y
        self.tiles_per_pixel_width = width
        self.tiles_per_pixel_height = height
        self.show_seconds = show_seconds
        self.military_time = military_time
        self.align_to_center = center

        # Validate and set pixel color; default to green if out of range
        self.pixel_color = (
            color
            if PixelColor.RED.value <= color <= PixelColor.BLACK.value
            else PixelColor.GREEN.value
        )

        self.tz_info: ZoneInfo = timezone
        self.stdscr: curses.window = None
        self.__clock_digits_qty = (
            5 + (3 if self.show_seconds else 0) + (3 if not self.military_time else 0)
        )
        self.__screen_height: int = 0
        self.__screen_width: int = 0
        self.__pixel_buffer: dict = {}
        self.__digit_buffer: list = []
        self.__top_corners: dict = {}
        self.slices: list[int | str] = []

    def __draw_pixel(self, pixel: str, x: int, y: int) -> None:
        """Draw a pixel at specified coordinates.

        Args:
            pixel (str): The pixel value ('1' for filled, '0' for empty).
            x (int): The x-coordinate for drawing.
            y (int): The y-coordinate for drawing.
        """

        color_pair = curses.color_pair(self.pixel_color)
        key = f"{x}:{y}"

        # Check if the pixel is already in the buffer and if it's different from the current one
        if key not in self.__pixel_buffer or self.__pixel_buffer[key] != pixel:
            self.__pixel_buffer[key] = pixel  # Save the current pixel state

            try:
                # Use '█' for filled pixels and space for empty ones
                self.stdscr.addch(y, x, "█" if pixel == "1" else " ", color_pair)
            except curses.error:
                # Remove from buffer if drawing fails due to terminal constraints
                self.__pixel_buffer.pop(key, None)

    @staticmethod
    def __colors_init() -> None:
        """Initialize color settings for terminal display."""

        curses.initscr()  # Initialize curses mode
        curses.start_color()  # Enable color functionality

        # Initialize default colors for use in the application
        curses.use_default_colors()

        # Initialize color pairs based on PixelColor enum values
        for color in PixelColor:
            curses.init_pair(color.value, getattr(curses, f"COLOR_{color.name}"), -1)

    def __interpolate(self, time_components: list[int | str]) -> None:
        """
        Draws a grid of symbols onto the display, updating only digits that have changed.

        Args:
            time_components (list[int | str]): The current clock digits to be displayed, either as integers or symbols.
        """
        # Flag to indicate if the screen needs to be refreshed after drawing
        update_the_screen = False

        # Iterate over each clock digit position to determine changes and update display
        for idx in range(self.__clock_digits_qty):
            # Only process the digit if it has changed from the previous state
            if time_components[idx] != self.__digit_buffer[idx]:

                # Indicate an element has changed
                update_the_screen = True

                # Convert the time component to its corresponding symbol representation
                symbols: list[str] = map_to_symbol(element=time_components[idx])

                # Store the updated digit in the buffer for future comparison
                self.__digit_buffer[idx] = time_components[idx]

                # Retrieve the starting position for the current digit
                current_line_position = self.__top_corners[f"dig{idx}_y"]

                # Draw each row in the symbol representation's height
                for row in range(SHAPE_HEIGHT):
                    column_position = self.__top_corners[f"dig{idx}_x"]

                    # Draw each column in the symbol representation's width
                    for col in range(SHAPE_WIDTH):
                        pixel_value = symbols.pop(0)
                        # Render tiles for each pixel value, scaled by user-defined tile dimensions
                        for tile_row in range(self.tiles_per_pixel_height):
                            for tile_col in range(self.tiles_per_pixel_width):
                                self.__draw_pixel(
                                    pixel=pixel_value,
                                    x=(column_position + tile_col),
                                    y=(current_line_position + tile_row),
                                )

                        # Move to the next column position by the width of a tile
                        column_position += self.tiles_per_pixel_width

                    # Move to the next row position by the height of a tile
                    current_line_position += self.tiles_per_pixel_height

        # Refresh the screen if any changes were drawnt
        if update_the_screen:
            self.stdscr.refresh()

    def __calculate_center_xy_position(self) -> None:
        """Calculate and adjust top-left position to center the clock on screen."""

        # Calculate dimensions needed for centering based on shape sizes and user settings
        pixel_height = SHAPE_HEIGHT * self.tiles_per_pixel_height
        pixel_width = SHAPE_WIDTH * self.tiles_per_pixel_width

        total_length_with_spaces = (
            self.__clock_digits_qty * pixel_width
            + (self.__clock_digits_qty - 1) * self.tiles_per_pixel_width
        )

        # Centering calculations based on available screen dimensions
        self.top_left_y = round((self.__screen_height - pixel_height) / 2)
        self.top_left_x = round((self.__screen_width - total_length_with_spaces) / 2)

    def __calculate_top_corners_position(self) -> None:
        """Set positions for each digit's top-left corner."""

        last_x = self.top_left_x

        for i in range(self.__clock_digits_qty):
            self.__top_corners[f"dig{i}_x"] = last_x
            self.__top_corners[f"dig{i}_y"] = self.top_left_y

            last_x += (
                SHAPE_WIDTH * self.tiles_per_pixel_width
                + self.tiles_per_pixel_width  # Space between symbols
            )

    def __check_fit(self) -> bool:
        """Check if the clock fits within available screen space.

        Returns:
            bool: True if it fits, False otherwise.
        """

        pixel_height = SHAPE_HEIGHT * self.tiles_per_pixel_height

        if (self.__screen_height - self.top_left_y) < pixel_height:
            return False

        pixel_width = SHAPE_WIDTH * self.tiles_per_pixel_width

        total_length_with_spaces = (
            self.__clock_digits_qty * pixel_width
            + (self.__clock_digits_qty - 1) * self.tiles_per_pixel_width
        )

        return (
            True
            if (self.__screen_width - self.top_left_x) >= total_length_with_spaces
            else False
        )

    def __handle_resize(self):
        """Handle terminal resizing events and adjust content accordingly."""

        # Update screen dimensions based on current window size
        self.__screen_height, self.__screen_width = self.stdscr.getmaxyx()

        if self.align_to_center:
            self.__calculate_center_xy_position()

        if not self.__check_fit():
            sys.exit(1)  # Exit if clock does not fit in resized window

        self.__calculate_top_corners_position()

        self.stdscr.clear()
        # Clear previous content and reset buffer
        self.__pixel_buffer.clear()
        # Pre-load the list with correct
        self.__digit_buffer: list = [" " for i in range(self.__clock_digits_qty)]

    def __application(self, stdscr: curses.window) -> None:
        """Main application logic that runs within curses environment."""

        self.stdscr = stdscr
        self.__handle_resize()

        # Initialize colors and cursor visibility settings
        self.__colors_init()
        curses.curs_set(0)

        # Create an instance of Quartz to manage time updates
        self.clock = Quartz(self.update, timezone=self.tz_info)

        try:
            while True:
                key = self.stdscr.getch()

                # Handle terminal resize events
                if curses.is_term_resized(self.__screen_height, self.__screen_width):
                    self.__handle_resize()
                    # Force a new interpolation to update the Display information with the last
                    # time information
                    self.__interpolate(time_components=self.slices)

                # Exit condition when 'q' or 'ESC' is pressed
                if key == ord("q") or key == 27:  # 27 is the ASCII code for ESC
                    break

        except KeyboardInterrupt:
            pass  # Gracefully handle Ctrl+C

        finally:
            # Clean up before exiting application
            self.stdscr.clear()
            if hasattr(self, "clock"):
                self.clock.stop()
            sys.exit(0)

    def update(self, current_time: datetime) -> None:
        """Update screen with current time representation.

        Args:
            current_time (datetime): The current time to be displayed on screen.
        """

        self.slices: list[int | str] = datetime_slicer(
            now=current_time,
            show_seconds=self.show_seconds,
            military_time=self.military_time,
        )

        # Interpolate symbols into pixels for display
        self.__interpolate(time_components=self.slices)

    def run(self) -> None:
        """Run the curses application within a wrapper."""

        try:
            curses.wrapper(self.__application)

        except curses.error:
            sys.exit(1)


def datetime_slicer(
    now: datetime, show_seconds: bool = False, military_time: bool = False
) -> list[int | str]:
    """Slice current datetime into individual components.

    Args:
        now (datetime): Current datetime object to be sliced.
        show_seconds (bool): Flag indicating whether to include seconds. Defaults to False.
        military_time (bool): Flag indicating whether to use military time format. Defaults to False.

    Returns:
        list[int | str]: A list containing hour, minute, second components along with separators.
    """

    hours = now.hour if military_time else int(now.strftime("%I"))
    am_pm_indicator = "" if military_time else now.strftime("%p")

    minutes = int(now.strftime("%M"))
    seconds_value: Optional[int] = int(now.strftime("%S")) if show_seconds else None

    # Prepare the output list
    output_list: list[int | str] = [
        hours // 10,
        hours % 10,
        ":",
        minutes // 10,
        minutes % 10,
    ]

    if show_seconds:
        output_list.extend(
            [
                ":",
                seconds_value // 10,
                seconds_value % 10,
            ]
        )

    if not military_time:
        output_list.append(" ")
        output_list.extend(list(am_pm_indicator))

    return output_list


def map_to_symbol(element: int | str) -> list[str]:
    """
    Convert a time component (either an integer or specific character) to its binary string representation.

    Args:
        element (int | str): An integer representing a digit (0-9) or a specific string character
                             (e.g., ":", " ", "A", "P", "M") for mapping to binary symbols.

    Returns:
        list[str]: A list of strings representing the binary form of the given time component.
    """
    # Check if the element is a character symbol and map accordingly
    if isinstance(element, str):
        # Map specific characters to their binary representations
        ret = list(
            {
                ":": COLON,  # Map colon character
                " ": SPACE,  # Map space character
                "A": LETTER_A,  # Map letter "A"
                "P": LETTER_P,  # Map letter "P"
                "M": LETTER_M,  # Map letter "M"
            }[element]
        )
    else:
        # Map integer digits to their binary representations
        ret = list(DIGIT[element])

    return ret
