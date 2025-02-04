import logging
from pathlib import Path
import random

import fastapi
from concurrent_log_handler import ConcurrentTimedRotatingFileHandler

import settings


def setup_uplink_gateway_logger():
    """
    This sets up a logger that is used record gateway information for each sensor
    uplink post message. It is a timed rotating file logger. A separate process
    reads the log files and posts them to a database. Thus the log files do
    not need to be kept for a long period of time.
    """
    # Create a logger object.
    logger = logging.getLogger("uplink_gateway_logger")
    logger.setLevel(logging.INFO)  # or DEBUG, WARNING, etc.

    # Create a timed rotating file handler.
    handler = ConcurrentTimedRotatingFileHandler(
        filename=Path(__file__).parent / "gtw-log/gtw.log",
        mode="a",
        when='M',
        interval=settings.UPLINK_LOG_FILE_ROTATION_TIME,
        backupCount=settings.UPLINK_LOG_FILE_BACKUP_COUNT
    )

    # Define a simple format that includes *only* the raw message text.
    # No timestamps, no log level, etc.
    formatter = logging.Formatter("%(message)s")

    # Apply the formatter to the handler.
    handler.setFormatter(formatter)

    # If the logger already has handlers, remove them so we don’t add duplicates.
    if logger.hasHandlers():
        logger.handlers.clear()

    # Add the new rotating file handler to the logger.
    logger.addHandler(handler)

    return logger


source = random.choice(['AHFC', 'ANTHC', 'AN'])


# Set up the gateway uplink message logger.
gtw_logger = setup_uplink_gateway_logger()

