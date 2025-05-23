# *****************************************************************************
# University of Southern Denmark
# Embedded C Programming (ECP)
#
# MODULENAME.: config.py
#
# PROJECT....: PPG pulsefreq. and -oximetry meas.
#
# DESCRIPTION:  
# A simple terminal application for collecting and exporting
# Biometric data. This module manages configuration settings for
# serial communication and database access.
#
# *****************************************************************************

import os
import json

# ********************** Constants ************************
COMPORT_CFG = "comport.cfg"
DEFAULT_COMPORT = "COM5"
DEFAULT_BAUDRATE = 115200

DB_CFG = "db.cfg"
DEFAULT_DB_CONFIG = {
    'host': "localhost",
    'user': "root",
    'password': "",
    'database': ""
}


def load_comport():
    """
    *******************************
    Function: load_comport
    -----------------------
    Reads the contents of the comport.cfg file and returns the COM port 
    and baud rate settings.

    Input:  None
    Output: Tuple (comport, baudrate)
    *******************************
    """
    if os.path.exists(COMPORT_CFG):
        try:
            with open(COMPORT_CFG, "r") as f:
                data = json.load(f)
                return data.get("comport", DEFAULT_COMPORT), data.get("baudrate", DEFAULT_BAUDRATE)
        except Exception:
            pass
    return DEFAULT_COMPORT, DEFAULT_BAUDRATE


def save_comport(comport, baudrate):
    """
    *******************************
    Function: save_comport
    -----------------------
    Saves the provided COM port and baud rate to a configuration file.

    Input:  comport   - COM port string (e.g. "COM3")
            baudrate  - Baud rate integer (e.g. 115200)
    Output: None
    *******************************
    """
    with open(COMPORT_CFG, "w") as f:
        json.dump({"comport": comport, "baudrate": baudrate}, f)


def load_db_config():
    """
    *******************************
    Function: load_db_config
    -------------------------
    Loads the database configuration from the db.cfg file if it exists.
    Returns default values if the file is missing or unreadable.

    Input:  None
    Output: Dictionary containing database config
    *******************************
    """
    if os.path.exists(DB_CFG):
        try:
            with open(DB_CFG, "r") as f:
                data = json.load(f)
                return {
                    'host': data.get('host', DEFAULT_DB_CONFIG['host']),
                    'user': data.get('user', DEFAULT_DB_CONFIG['user']),
                    'password': data.get('password', DEFAULT_DB_CONFIG['password']),
                    'database': data.get('database', DEFAULT_DB_CONFIG['database'])
                }
        except Exception:
            pass
    return DEFAULT_DB_CONFIG.copy()


def save_db_config(db_config):
    """
    *******************************
    Function: save_db_config
    -------------------------
    Saves the given database configuration dictionary to a file.

    Input:  db_config - Dictionary containing keys: host, user, password, database
    Output: None
    *******************************
    """
    with open(DB_CFG, "w") as f:
        json.dump(db_config, f)


# ********************** Runtime Initialization ***********************
COMPORT, BAUDRATE = load_comport()
DB_CONFIG = load_db_config()
