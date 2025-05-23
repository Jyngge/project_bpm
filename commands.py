# *****************************************************************************
# University of Southern Denmark
# Embedded C Programming (ECP)
#
# MODULENAME.: commands.py
#
# PROJECT....: PPG pulsefreq. and -oximetry meas.
#
# DESCRIPTION:  
# A simple terminal application for collecting and exporting
# biometric data. This module handles command execution and user
# interaction through the terminal interface.
# *****************************************************************************

import os
import sys
import csv
from datetime import datetime
from config import save_comport, COMPORT, BAUDRATE
from database import (
    add_user, remove_user, get_user_id, get_all_bpm_logs, get_user_bpm_logs,
    get_all_oxygen_logs, get_user_oxygen_logs, delete_logs
)
from serial_handler import log_bio


def clear():
    """
    *******************************
    Function: clear
    -------------------
    Clears the terminal screen output.

    Input:  None
    Output: None
    *******************************
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def get_available_commands():
    """
    *******************************
    Function: get_available_commands
    -------------------
    Returns a dictionary of available commands and their descriptions.

    Input:  None
    Output: dict[str, str]
    *******************************
    """
    return {
        'add_user':     'Add a new user to the system',
        'remove_user':  'Remove an existing user from the system',
        'set_user':     'Set the current user',
        'show_bpm_log': 'Show the BPM log of users',
        'show_oxygen_log': 'Show the oxygen level log of users',
        'log_bio':      'Log Bio-Metrics data from the COM port',
        'output_to_csv':'Output the BPM and oxygen logs to a CSV file',
        'set_comport':  'Set the COM port and baudrate for UART communication',
        'delete_logs':  'Delete logs for a specific user or all users',
        'help':         'Show available commands',
        'clear':        'Clear the console output',
        'exit':         'Exit the application'
    }


def execute_command(command):
    """
    *******************************
    Function: execute_command
    -------------------
    Processes user input and executes the appropriate action based on the command.

    Input:  command (str) - The user's input command
    Output: None
    *******************************
    """
    cmd = command.lower()
    if cmd == 'add_user':
        username = input("Enter username: ").strip()
        age = int(input("Enter age: ").strip())
        add_user(username, age)
        print(f"User '{username}' added successfully.")
    elif cmd == 'remove_user':
        username = input("Enter username to remove: ").strip()
        remove_user(username)
        print(f"User '{username}' removed successfully.")
    elif cmd == 'set_user':
        username = input("Enter username to set as current user: ").strip()
        user_id = get_user_id(username)
        if user_id:
            current_user['id'] = user_id
            print(f"Current user set to '{username}' (ID: {user_id}).")
        else:
            print(f"User '{username}' not found.")
    elif cmd == 'show_bpm_log':
        username = input("Enter username to view BPM logs or 'all' to view all users' BPM logs: ").strip().lower()
        if username == "all":
            rows = get_all_bpm_logs()
            if rows:
                print("BPM log for all users (sorted by username):")
                for username, bpm, timestamp in rows:
                    print(f"Username: {username}, BPM: {bpm}, Timestamp: {timestamp}")
            else:
                print("No BPM logs found.")
        else:
            rows = get_user_bpm_logs(username)
            if rows:
                print(f"BPM log for user '{username}' (sorted by timestamp):")
                for bpm, timestamp in rows:
                    print(f"BPM: {bpm}, Timestamp: {timestamp}")
            else:
                print(f"No BPM log found for user '{username}'.")
    elif cmd == 'show_oxygen_log':
        username = input("Enter username to view oxygen level logs or 'all' to view all users' oxygen level logs: ").strip().lower()
        if username == "all":
            rows = get_all_oxygen_logs()
            if rows:
                print("Oxygen level log for all users (sorted by username):")
                for username, oxygen_level, timestamp in rows:
                    print(f"Username: {username}, Oxygen Level: {oxygen_level}%, Timestamp: {timestamp}")
            else:
                print("No oxygen level logs found.")
        else:
            rows = get_user_oxygen_logs(username)
            if rows:
                print(f"Oxygen level log for user '{username}' (sorted by timestamp):")
                for oxygen_level, timestamp in rows:
                    print(f"Oxygen Level: {oxygen_level}%, Timestamp: {timestamp}")
            else:
                print(f"No oxygen level log found for user '{username}'.")
    elif cmd == 'log_bio':
        if current_user['id'] is None:
            print("No user is currently logged in. Please set a user first.")
        else:
            log_bio(current_user['id'])
    elif cmd == 'output_to_csv':
        output_to_csv()
    elif cmd == 'set_comport':
        comport = input(f"Enter the COM port (current: {COMPORT}): ").strip() or COMPORT
        try:
            baudrate = int(input(f"Enter the baud rate (current: {BAUDRATE}): ").strip() or BAUDRATE)
        except ValueError:
            print("Invalid baudrate. Keeping previous value.")
            baudrate = BAUDRATE
        save_comport(comport, baudrate)
        print(f"COM port set to '{comport}' with baud rate '{baudrate}'. Please restart the program for changes to take effect.")
    elif cmd == 'delete_logs':
        username = input("Enter the username to delete logs for, or 'all' to delete logs for all users: ").strip().lower()
        if username == "all":
            delete_logs()
            print("All logs have been deleted.")
        else:
            user_id = get_user_id(username)
            if user_id:
                delete_logs(user_id)
                print(f"Logs for user '{username}' have been deleted.")
            else:
                print(f"User '{username}' not found.")
    elif cmd == 'clear':
        clear()
    elif cmd == 'help':
        print("Available commands:")
        for cmd, desc in get_available_commands().items():
            print(f"{cmd}: {desc}")
    elif cmd == 'exit':
        print("Exiting the application.")
        sys.exit(0)
    else:
        print(f"Unknown command: {command}. Type 'help' for a list of commands.")


def output_to_csv():
    """
    *******************************
    Function: output_to_csv
    -------------------
    Exports BPM and/or oxygen logs to a timestamped CSV file.
    User can choose to export data for a specific user or all users.

    Input:  None
    Output: CSV file(s) created in script directory
    *******************************
    """
    try:
        if getattr(sys, 'frozen', False):
            script_dir = os.path.dirname(sys.executable)
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))

        data_type = input("Enter 'bpm' to export BPM logs, 'oxygen' to export oxygen level logs, or 'all' to export both: ").strip().lower()
        if data_type not in ['bpm', 'oxygen', 'all']:
            print("Invalid option. Please enter 'bpm', 'oxygen', or 'all'.")
            return

        username = input("Enter the username or 'all' to export logs: ").strip().lower()

        if data_type in ['bpm', 'all']:
            if username == "all":
                rows = get_all_bpm_logs()
                if not rows:
                    print("No BPM logs found.")
                else:
                    filename = os.path.join(script_dir, f"bpm_logs_all_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
                    header = ["Username", "BPM", "Timestamp"]
                    with open(filename, mode="w", newline="", encoding="utf-8") as file:
                        writer = csv.writer(file)
                        writer.writerow(header)
                        writer.writerows(rows)
                    print(f"BPM logs successfully exported to '{filename}'.")
            else:
                rows = get_user_bpm_logs(username)
                if not rows:
                    print(f"No BPM logs found for user '{username}'.")
                else:
                    filename = os.path.join(script_dir, f"bpm_logs_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
                    header = ["BPM", "Timestamp"]
                    with open(filename, mode="w", newline="", encoding="utf-8") as file:
                        writer = csv.writer(file)
                        writer.writerow(header)
                        writer.writerows(rows)
                    print(f"BPM logs successfully exported to '{filename}'.")

        if data_type in ['oxygen', 'all']:
            if username == "all":
                rows = get_all_oxygen_logs()
                if not rows:
                    print("No oxygen level logs found.")
                else:
                    filename = os.path.join(script_dir, f"oxygen_logs_all_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
                    header = ["Username", "Oxygen Level", "Timestamp"]
                    with open(filename, mode="w", newline="", encoding="utf-8") as file:
                        writer = csv.writer(file)
                        writer.writerow(header)
                        writer.writerows(rows)
                    print(f"Oxygen level logs successfully exported to '{filename}'.")
            else:
                rows = get_user_oxygen_logs(username)
                if not rows:
                    print(f"No oxygen level logs found for user '{username}'.")
                else:
                    filename = os.path.join(script_dir, f"oxygen_logs_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
                    header = ["Oxygen Level", "Timestamp"]
                    with open(filename, mode="w", newline="", encoding="utf-8") as file:
                        writer = csv.writer(file)
                        writer.writerow(header)
                        writer.writerows(rows)
                    print(f"Oxygen level logs successfully exported to '{filename}'.")
    except Exception as e:
        print(f"Error exporting logs to CSV: {e}")

# ******************** Variables ************************
current_user = {'id': None}
