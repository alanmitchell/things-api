import logging
from concurrent_log_handler import ConcurrentTimedRotatingFileHandler
from pathlib import Path
import random

from dateutil.parser import parse

# maximum size of each individual log file.
MAX_BYTES = 10000


def setup_logger(log_file_path, max_bytes=MAX_BYTES, backup_count=5):
    """
    Sets up a rotating file logger that:
      - Rotates when file size reaches `max_bytes`.
      - Keeps up to `backup_count` old log files.
      - Outputs only the raw message on each line (no timestamps).
    """
    # Create a logger object.
    logger = logging.getLogger("gateway_logger")
    logger.setLevel(logging.INFO)  # or DEBUG, WARNING, etc.

    # Create a timed rotating file handler.
    handler = ConcurrentTimedRotatingFileHandler(
        filename=log_file_path,
        mode="a",
        when='M',
        interval=15,
        backupCount=backup_count
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


def parse_and_log(things_uplink_message):
    """Parses the desirable information from a Things v3 JSON uplink message and records
    in the log file.
    """
    rec = things_uplink_message
    gtw_recs = []  # holds gateway records

    dev_id = rec["end_device_ids"]["device_id"]
    dev_eui = rec["end_device_ids"]["dev_eui"]
    ctr = rec["uplink_message"]["f_cnt"]
    ts = int(parse(rec["received_at"]).timestamp())
    dr = rec["uplink_message"]["settings"]["data_rate"]["lora"]
    data_rate = f"SF{dr['spreading_factor']}BW{int(dr['bandwidth'] / 1000)}"

    # add to list of gateway records
    for gtw in rec["uplink_message"]["rx_metadata"]:
        r = {}
        r["gtw_id"] = gtw["gateway_ids"]["gateway_id"]
        r["gtw_eui"] = gtw["gateway_ids"]["eui"]
        r["snr"] = gtw["snr"]
        r["rssi"] = gtw["rssi"]
        gtw_recs.append(r)

    source = random.choice(['AHFC', 'ANTHC', 'AN'])
    for gtw in gtw_recs:
        r = f"{source},{ts},{dev_id},{dev_eui},{ctr},{gtw['gtw_id']},{gtw['gtw_eui']},{gtw['snr']},{gtw['rssi']},{data_rate}"
        logger.info(r)


# Set up the logger.
logger = setup_logger(log_file_path=Path(__file__).parent / "data/gtw-record.log")


if __name__=="__main__":
    msg = open("test.json").read()
    from json import loads

    parse_and_log(loads(msg))
