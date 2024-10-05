# Buit-in libraries
#
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
import threading
from time import sleep
import sys

# Custom-made libraries
#


logger = logging.getLogger(__name__)


class TimeBeat(threading.Thread):
    """Engine class responsible for periodically updating the screen with a timestamp.

    This class runs in a separate thread, fetching the current system timestamp
    every second, taking into account the specified timezone if provided. It invokes
    the provided `update` method to refresh the screen with the new timestamp until
    stopped.
    """

    def __init__(self, update: callable, tz: ZoneInfo = None) -> None:
        """Initialize the Engine thread.

        Args:
            update (callable): A function that will be called with the current
            Unix timestamp each second to update the screen.
            tz (timezone, optional): The timezone to use for fetching the timestamp.
            If not provided, the system's local timezone will be used.
        """
        super().__init__(name="Clock beat", daemon=True)
        self.update = update  # Function to update the screen with the timestamp
        self.tz_info = tz  # Timezone information (can be None for local timezone)
        self.__stop_event = threading.Event()  # Event to signal thread termination
        self.start()  # Start the thread immediately after initialization

    def run(self) -> None:
        """Main loop of the Engine thread.

        Continuously fetches the current system timestamp, respecting the provided
        timezone (or defaulting to the system's local timezone), and calls the `update`
        function with it every second. The loop continues until the stop event is set.
        Logs a message when the thread terminates.

        Raises:
            Exception: Catches and logs any exception that occurs during execution,
            terminating the program if an error arises.
        """
        try:
            while not self.__stop_event.is_set():
                now = datetime.now(
                    tz=self.tz_info
                )  # Get the current date and time with timezone
                timestamp = int(now.timestamp())  # Convert the time to a Unix timestamp
                self.update(timestamp)  # Call the update function with the timestamp
                sleep(1)  # Pause for one second before the next update

            logger.info("Screen update thread stopped.")

        except threading.ThreadError as e:
            logging.error(f"An error occurred during the thread operation: {e}")
            sys.exit(1)  # Exit the program in case of an error

    def stop(self) -> None:
        """Stop the Engine thread.

        Sets the stop event, signaling the thread to exit the main loop and terminate gracefully.
        """
        self.__stop_event.set()  # Signal the thread to stop
