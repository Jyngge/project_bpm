import os
import json

# --- COM Port Config ---
COMPORT_CFG = "comport.cfg"
DEFAULT_COMPORT = "COM5"
DEFAULT_BAUDRATE = 115200

def load_comport():
    if os.path.exists(COMPORT_CFG):
        try:
            with open(COMPORT_CFG, "r") as f:
                data = json.load(f)
                return data.get("comport", DEFAULT_COMPORT), data.get("baudrate", DEFAULT_BAUDRATE)
        except Exception:
            pass
    return DEFAULT_COMPORT, DEFAULT_BAUDRATE

def save_comport(comport, baudrate):
    with open(COMPORT_CFG, "w") as f:
        json.dump({"comport": comport, "baudrate": baudrate}, f)

COMPORT, BAUDRATE = load_comport()

# --- DB Config ---
DB_CFG = "db.cfg"
DEFAULT_DB_CONFIG = {
    'host': "localhost",
    'user': "root",
    'password': "",
    'database': ""
}

def load_db_config():
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
    with open(DB_CFG, "w") as f:
        json.dump(db_config, f)

DB_CONFIG = load_db_config()