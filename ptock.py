#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Buit-in libraries
#
import logging
from zoneinfo import ZoneInfo

# Custom-made libraries
#
from ptock_display import ScreenConnector

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def ptock() -> None:
    """ """
    tz = ZoneInfo("America/Argentina/Buenos_Aires")  # Set to Buenos  Aires, Argentina.
    screen = ScreenConnector(tz=tz)
    screen.run()


if __name__ == "__main__":
    ptock()
