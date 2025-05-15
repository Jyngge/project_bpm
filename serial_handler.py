# *****************************************************************************
# University of Southern Denmark
# Embedded C Programming (ECP)
#
# MODULENAME.: serial_handler.py
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

import serial
import threading
import msvcrt
from datetime import datetime
from config import COMPORT, BAUDRATE
from database import log_bpm, log_oxygen_level

def log_bio(current_user_id):
# **********************************************
# Input    : Current user set ID. ID's are defined in the database.
# Output   : Sends the data to the database.
# Function : Activates the serial port and listens for incoming data.
#            The data is expected to be in the format "bpm:<value>oxy:<value>".
#            The function will log the data to the database under the user set by the program.
# **********************************************
    print("Entering Bio-Metrics logging mode. Press 'Esc' to exit.")
    exit_flag = threading.Event()

    def uart_listener():
        try:
            ser = serial.Serial(COMPORT, BAUDRATE, timeout=1)
            print(f"Listening on {COMPORT} at {BAUDRATE} baud...")
            while not exit_flag.is_set():
                line = ser.readline().decode('utf-8').strip()
                if not line:
                    continue
                try:
                    if "bpm:" in line and "oxy:" in line:
                        bpm_index = line.find("bpm:")
                        oxy_index = line.find("oxy:")
                        if bpm_index < oxy_index:
                            bpm_part = line[bpm_index:oxy_index].strip()
                            oxy_part = line[oxy_index:].trip()
                        else:
                            oxy_part = line[oxy_index:bpm_index].strip()
                            bpm_part = line[bpm_index:].strip()
                        if bpm_part.startswith("bpm:"):
                            bpm = int(bpm_part.split(":")[1].strip())
                            log_bpm(current_user_id, bpm, datetime.now())
                        if oxy_part.startswith("oxy:"):
                            oxygen_level = int(oxy_part.split(":")[1].strip())
                            log_oxygen_level(current_user_id, oxygen_level, datetime.now())
                    elif line.startswith("bpm:"):
                        bpm = int(line.split(":")[1].strip())
                        log_bpm(current_user_id, bpm, datetime.now())
                    elif line.startswith("oxy:"):
                        oxygen_level = int(line.split(":")[1].strip())
                        log_oxygen_level(current_user_id, oxygen_level, datetime.now())
                except (ValueError, IndexError):
                    print("Error parsing data. Ensure the format is correct.")
        except serial.SerialException as e:
            print(f"Serial error: {e}")
        finally:
            if 'ser' in locals() and ser.is_open:
                ser.close()

    listener_thread = threading.Thread(target=uart_listener)
    listener_thread.start()

    while not exit_flag.is_set():
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'\x1b':
                print("Exiting Bio-Metrics logging mode.")
                exit_flag.set()
    listener_thread.join()