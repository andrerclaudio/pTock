# Built-in libraries
import sys
import threading
from datetime import datetime
from time import sleep
from typing import Optional, Callable
from zoneinfo import ZoneInfo


class Quartz(threading.Thread):
    """
    A thread that periodically updates the screen with the current timestamp, functioning like a clock.

    This thread retrieves the current timestamp every second, using a specified timezone if provided,
    and invokes the supplied `update` method to refresh the display until it is stopped.
    """

    def __init__(
        self, update: Callable[[datetime], None], timezone: Optional[ZoneInfo] = None
    ) -> None:
        """
        Initialize the Quartz thread.

        Args:
            update (Callable[[datetime], None]): A callback function that takes a datetime object
                                                  to update the screen display.
            timezone (Optional[ZoneInfo]): The timezone to be used for timestamps. Defaults to UTC
                                            if no timezone is specified.
        """
        super().__init__(name="QuartzClock", daemon=True)
        self.update_callback = update
        self.timezone_info = timezone or ZoneInfo(
            "UTC"
        )  # Default to UTC if no timezone is provided
        self.__stop_event = threading.Event()
        self.start()  # Start the thread upon initialization

    def run(self) -> None:
        """
        The main loop of the Quartz thread.

        Continuously fetches the current timestamp based on the provided timezone (or defaults to UTC),
        and calls the `update` function with it every second until the thread is stopped.
        """
        try:
            last_timestamp = int(0)  # Init the variable

            while True:  # Loop forever

                current_time = datetime.now(tz=self.timezone_info)  # Get current time
                current_timestamp = int(
                    current_time.timestamp()
                )  # Get current timestamp

                # Call update if the timestamp has changed since last check
                if current_timestamp != last_timestamp:
                    self.update_callback(current_time)  # Update display with new time
                    last_timestamp = current_timestamp  # Update last timestamp
                # Sleep until next check
                sleep(0.1)

        except threading.ThreadError as error:
            sys.exit(1)  # Exit program in case of a threading error

    def stop(self) -> None:
        """Stops the Quartz thread by setting the stop event."""
        self.__stop_event.set()  # Signal the thread to stop
