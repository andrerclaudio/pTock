#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Buit-in libraries
#
import logging
from zoneinfo import ZoneInfo

# Custom-made libraries
#
from view import ViewConnector

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def ptock() -> None:
    """ """
    tz = ZoneInfo("America/Argentina/Buenos_Aires")  # Set to Buenos  Aires, Argentina.
    clock = ViewConnector(timezone=tz)
    clock.run()


if __name__ == "__main__":
    ptock()
