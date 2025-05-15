# *****************************************************************************
# University of Southern Denmark
# Embedded C Programming (ECP)
#
# MODULENAME.: config.py
#
# PROJECT....: Semester Project 4
#
# DESCRIPTION:  A simple terminal application for collecting and and exporting
#               Biometric data.
#
# Change Log:
# *****************************************************************************
# Date    Id          Change
# 020525  Majur22     Module created.
# 
# *****************************************************************************

import os
import json

def load_comport():
# **********************************************
# Input    : Contents of the comport.cfg file if it exists.
# Output   :
# Function : Reads the contents of the comport.cfg file and returns the COM port and baud rate.
# **********************************************
    if os.path.exists(COMPORT_CFG):
        try:
            with open(COMPORT_CFG, "r") as f:
                data = json.load(f)
                return data.get("comport", DEFAULT_COMPORT), data.get("baudrate", DEFAULT_BAUDRATE)
        except Exception:
            pass
    return DEFAULT_COMPORT, DEFAULT_BAUDRATE

def save_comport(comport, baudrate):
# **********************************************
# Input    : 
# Output   :
# Function : Saves the COM port and baud rate to a cfg file.
# **********************************************
    with open(COMPORT_CFG, "w") as f:
        json.dump({"comport": comport, "baudrate": baudrate}, f)


def load_db_config():
# **********************************************
# Input    : 
# Output   :
# Function : Reads the contents of the db.cfg file if it exists.
# **********************************************
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
# **********************************************
# Input    : 
# Output   :
# Function : Saves the database configuration to a cfg file.
# **********************************************
    with open(DB_CFG, "w") as f:
        json.dump(db_config, f)



COMPORT_CFG = "comport.cfg"
DEFAULT_COMPORT = "COM5"
DEFAULT_BAUDRATE = 115200
COMPORT, BAUDRATE = load_comport()

DB_CFG = "db.cfg"
DEFAULT_DB_CONFIG = {
    'host': "localhost",
    'user': "root",
    'password': "",
    'database': ""
}
DB_CONFIG = load_db_config()

