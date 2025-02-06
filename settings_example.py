"""Template for the actual "settings.py" file, which holds the settings for 
the application. Do not include the actual "settings.py" file in source control.
"""

# Valid API Keys and the corresponding source of the request.
API_KEYS = {
    "ABC": "someone",
    "CDE": "somebody else"
}

# ----- Settings for logging Things Network uplink posts.

# Number of minutes for log file rotation, which then causes the
# rotated log file to be posted to the MotherDuck database.
UPLINK_LOG_FILE_ROTATION_TIME = 5

# Number of log file backups to keep
UPLINK_LOG_FILE_BACKUP_COUNT = 12

