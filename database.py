# *****************************************************************************
# University of Southern Denmark
# Embedded C Programming (ECP)
#
# MODULENAME.: database.py
#
# PROJECT....: PPG pulsefreq. and -oximetry meas.
#
# DESCRIPTION:  
# A simple terminal application for collecting and exporting
# biometric data. This module handles all interactions with
# the MySQL database, including user and data management.
# *****************************************************************************

import mysql.connector
from config import DB_CONFIG, save_db_config, load_db_config


def prompt_db_config():
    """
    *******************************
    Function: prompt_db_config
    -------------------
    Prompts the user for database connection settings if the current config fails.

    Input:  None
    Output: dict - New database configuration
    *******************************
    """
    print("Database connection failed. Please enter new database settings:")
    host = input("Host (default: localhost): ").strip() or "localhost"
    user = input("User (default: root): ").strip() or "root"
    password = input("Password: ").strip()
    database = input("Database name (default: bio_metric_database): ").strip() or "bio_metric_database"
    db_config = {
        'host': host,
        'user': user,
        'password': password,
        'database': database
    }
    save_db_config(db_config)
    return db_config


def connect_db():
    """
    *******************************
    Function: connect_db
    -------------------
    Attempts to connect to the MySQL database using config from file.
    If connection fails, prompts user for updated settings.

    Input:  None
    Output: mysql.connector.MySQLConnection
    *******************************
    """
    config = DB_CONFIG
    while True:
        try:
            return mysql.connector.connect(**config)
        except mysql.connector.Error as e:
            print(f"Error connecting to database: {e}")
            config = prompt_db_config()


def add_user(username, age):
    """
    *******************************
    Function: add_user
    -------------------
    Adds a new user with the given username and age to the database.

    Input:  username (str), age (int)
    Output: None
    *******************************
    """
    cursor = conn.cursor()
    query = "INSERT INTO user (username, age) VALUES (%s, %s)"
    cursor.execute(query, (username, age))
    conn.commit()
    cursor.close()


def remove_user(username):
    """
    *******************************
    Function: remove_user
    -------------------
    Deletes a user from the database by username.

    Input:  username (str)
    Output: None
    *******************************
    """
    cursor = conn.cursor()
    query = "DELETE FROM user WHERE username = %s"
    cursor.execute(query, (username,))
    conn.commit()
    cursor.close()


def get_user_id(username):
    """
    *******************************
    Function: get_user_id
    -------------------
    Retrieves a user’s ID based on their username.

    Input:  username (str)
    Output: int or None - User ID
    *******************************
    """
    cursor = conn.cursor()
    query = "SELECT id FROM user WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None


def log_bpm(user_id, bpm, timestamp):
    """
    *******************************
    Function: log_bpm
    -------------------
    Logs a BPM value for a user into the bpm_table.

    Input:  user_id (int), bpm (int), timestamp (datetime)
    Output: None
    *******************************
    """
    cursor = conn.cursor()
    query = "INSERT INTO bpm_table (userID, bpm, time_stamp) VALUES (%s, %s, %s)"
    cursor.execute(query, (user_id, bpm, timestamp))
    conn.commit()
    cursor.close()


def log_oxygen_level(user_id, oxygen_level, timestamp):
    """
    *******************************
    Function: log_oxygen_level
    -------------------
    Logs an oxygen level for a user into the oxygen_level_table.

    Input:  user_id (int), oxygen_level (int), timestamp (datetime)
    Output: None
    *******************************
    """
    cursor = conn.cursor()
    query = "INSERT INTO oxygen_level_table (userID, oxygen_level, time_stamp) VALUES (%s, %s, %s)"
    cursor.execute(query, (user_id, oxygen_level, timestamp))
    conn.commit()
    cursor.close()


def get_all_bpm_logs():
    """
    *******************************
    Function: get_all_bpm_logs
    -------------------
    Retrieves BPM logs for all users.

    Input:  None
    Output: list of tuples (username, bpm, timestamp)
    *******************************
    """
    cursor = conn.cursor()
    query = """
        SELECT user.username, bpm_table.bpm, bpm_table.time_stamp 
        FROM bpm_table 
        INNER JOIN user ON bpm_table.userID = user.id
        ORDER BY user.username, bpm_table.time_stamp
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    return rows


def get_user_bpm_logs(username):
    """
    *******************************
    Function: get_user_bpm_logs
    -------------------
    Retrieves BPM logs for a specific user.

    Input:  username (str)
    Output: list of tuples (bpm, timestamp)
    *******************************
    """
    cursor = conn.cursor()
    query = """
        SELECT bpm_table.bpm, bpm_table.time_stamp 
        FROM bpm_table 
        INNER JOIN user ON bpm_table.userID = user.id 
        WHERE user.username = %s
        ORDER BY bpm_table.time_stamp
    """
    cursor.execute(query, (username,))
    rows = cursor.fetchall()
    cursor.close()
    return rows


def get_all_oxygen_logs():
    """
    *******************************
    Function: get_all_oxygen_logs
    -------------------
    Retrieves oxygen level logs for all users.

    Input:  None
    Output: list of tuples (username, oxygen_level, timestamp)
    *******************************
    """
    cursor = conn.cursor()
    query = """
        SELECT user.username, oxygen_level_table.oxygen_level, oxygen_level_table.time_stamp 
        FROM oxygen_level_table 
        INNER JOIN user ON oxygen_level_table.userID = user.id
        ORDER BY user.username, oxygen_level_table.time_stamp
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    return rows


def get_user_oxygen_logs(username):
    """
    *******************************
    Function: get_user_oxygen_logs
    -------------------
    Retrieves oxygen level logs for a specific user.

    Input:  username (str)
    Output: list of tuples (oxygen_level, timestamp)
    *******************************
    """
    cursor = conn.cursor()
    query = """
        SELECT oxygen_level_table.oxygen_level, oxygen_level_table.time_stamp 
        FROM oxygen_level_table 
        INNER JOIN user ON oxygen_level_table.userID = user.id 
        WHERE user.username = %s
        ORDER BY oxygen_level_table.time_stamp
    """
    cursor.execute(query, (username,))
    rows = cursor.fetchall()
    cursor.close()
    return rows


def delete_logs(user_id=None):
    """
    *******************************
    Function: delete_logs
    -------------------
    Deletes all logs, or logs for a specific user, from the database.

    Input:  user_id (int or None)
    Output: None
    *******************************
    """
    cursor = conn.cursor()
    if user_id is None:
        cursor.execute("DELETE FROM bpm_table")
        cursor.execute("DELETE FROM oxygen_level_table")
    else:
        cursor.execute("DELETE FROM bpm_table WHERE userID = %s", (user_id,))
        cursor.execute("DELETE FROM oxygen_level_table WHERE userID = %s", (user_id,))
    conn.commit()
    cursor.close()


# ******************** Runtime Initialization ********************
conn = connect_db()
