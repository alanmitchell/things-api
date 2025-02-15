"""Main script for the Things API application. Receives and processes
HTTP requests. Starts a thread that stores Things message data into a
database.
"""
import logging
from pathlib import Path
from typing import Any
import time
import threading

from fastapi import FastAPI, Body, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from concurrent_log_handler import ConcurrentTimedRotatingFileHandler

import settings
import things_parser
import uplink_to_db


# Create a security dependency that looks for the API key in the header.
# This expects an API key in the "store-key" header.
api_key_header = APIKeyHeader(name="store-key", auto_error=True)

app = FastAPI()

async def validate_api_key(api_key: str = Security(api_key_header)):
    """Used to validate the API key.  Returns the source of the request,
    if a valid API key is provided.
    """
    if api_key not in settings.API_KEYS.keys():
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    else:
        source = settings.API_KEYS[api_key]
    
    return source

@app.get('/')
async def index():
    return {"message": "Things API Home page."}

@app.post('/store-uplink')
async def store_uplink(payload: Any = Body(...), source: str = Depends(validate_api_key)):
    try:
        recs = things_parser.parse_uplink_gateway_info(payload, source)
        for rec in recs:
            gtw_logger.info(rec)

        return {"message": f"OK, {len(recs)} records added"}
    except:
        raise HTTPException(
            status_code=400,  # Bad Request
            detail="Error in processing uplink data."
        )
        

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

def periodically_write_to_db():
    """Start a thread to check whether there are Things message log files 
    ready to be written to the database
    """
    while True:
        try:
            uplink_to_db.check_for_complete_log_files()
            time.sleep(60)    # check every minute
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(10)


# Set up the gateway uplink message logger.
gtw_logger = setup_uplink_gateway_logger()

# start a thread to periodically check for complete Things message log 
# files that need to be written to the database.
thread = threading.Thread(target=periodically_write_to_db, daemon=True)
thread.start()

