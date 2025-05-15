# *****************************************************************************
# University of Southern Denmark
# Embedded C Programming (ECP)
#
# MODULENAME.: database.py
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


import mysql.connector
from config import DB_CONFIG, save_db_config, load_db_config


def prompt_db_config():
# **********************************************
# Input    : 
# Output   :
# Function : Prompts the user for database connection settings if the connection fails.
# **********************************************
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
# **********************************************
# Input    : 
# Output   :
# Function : Connects to the MySQL database using the provided configuration.
# **********************************************
    config = DB_CONFIG
    while True:
        try:
            return mysql.connector.connect(**config)
        except mysql.connector.Error as e:
            print(f"Error connecting to database: {e}")
            config = prompt_db_config()


def add_user(username, age):
# **********************************************
# Input    : Username and age of the user.
# Output   :
# Function : Adds a new user to the database.
# **********************************************
    cursor = conn.cursor()
    query = "INSERT INTO user (username, age) VALUES (%s, %s)"
    cursor.execute(query, (username, age))
    conn.commit()
    cursor.close()

def remove_user(username):
# **********************************************
# Input    : Username of the user to be removed.
# Output   :
# Function : Removes a user from the database.
# **********************************************
    cursor = conn.cursor()
    query = "DELETE FROM user WHERE username = %s"
    cursor.execute(query, (username,))
    conn.commit()
    cursor.close()

def get_user_id(username):
# **********************************************
# Input    : Username of the user.
# Output   : User ID of the user.
# Function : Retrieves the user ID from the database based on the username.
# **********************************************
    cursor = conn.cursor()
    query = "SELECT id FROM user WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None

def log_bpm(user_id, bpm, timestamp):
# **********************************************
# Input    : User ID, BPM value, and timestamp.
# Output   :
# Function : Logs the BPM data to the database.
# **********************************************
    cursor = conn.cursor()
    query = "INSERT INTO bpm_table (userID, bpm, time_stamp) VALUES (%s, %s, %s)"
    cursor.execute(query, (user_id, bpm, timestamp))
    conn.commit()
    cursor.close()

def log_oxygen_level(user_id, oxygen_level, timestamp):
# **********************************************
# Input    : User ID, oxygen level value, and timestamp.
# Output   :
# Function : Logs the oxygen level data to the database.
# **********************************************
    cursor = conn.cursor()
    query = "INSERT INTO oxygen_level_table (userID, oxygen_level, time_stamp) VALUES (%s, %s, %s)"
    cursor.execute(query, (user_id, oxygen_level, timestamp))
    conn.commit()
    cursor.close()


def get_all_bpm_logs():
# **********************************************
# Input    :
# Output   :
# Function : Retrieves all BPM logs from the database. 
# **********************************************
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
# **********************************************
# Input    : Username of the user.
# Output   :
# Function : Retrieves BPM logs for a specific user from the database.
# **********************************************
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
# **********************************************
# Input    : 
# Output   :
# Function : Retrieves all oxygen level logs from the database.
# **********************************************
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
# **********************************************
# Input    : 
# Output   :
# Function : Retrieves oxygen level logs for a specific user from the database.
# **********************************************
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
# **********************************************
# Input    : User ID of the user whose logs are to be deleted. If None, all logs will be deleted.
# Output   :
# Function : Deletes all logs from the database or logs for a specific user.
# **********************************************
    cursor = conn.cursor()
    if user_id is None:
        cursor.execute("DELETE FROM bpm_table")
        cursor.execute("DELETE FROM oxygen_level_table")
    else:
        cursor.execute("DELETE FROM bpm_table WHERE userID = %s", (user_id,))
        cursor.execute("DELETE FROM oxygen_level_table WHERE userID = %s", (user_id,))
    conn.commit()
    cursor.close()


    conn = connect_db()