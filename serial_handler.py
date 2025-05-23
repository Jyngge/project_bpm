# *****************************************************************************
# University of Southern Denmark
# Embedded C Programming (ECP)
#
# MODULENAME.: serial_handler.py
#
# PROJECT....: PPG pulsefreq. and -oximetry meas.
#
# DESCRIPTION:  
# A simple terminal application for collecting and exporting
# biometric data from a serial interface. This module reads real-time
# heart rate and oxygen saturation from a microcontroller and logs the
# results to a database.
#
# *****************************************************************************

import serial
import threading
import msvcrt
from datetime import datetime
from config import COMPORT, BAUDRATE
from database import log_bpm, log_oxygen_level


def log_bio(current_user_id, username="user"):
    """
    *******************************
    Function: log_bio
    -------------------
    Opens the serial port and listens for biometric data.
    Expects input lines in the format: "bpm:<value>oxy:<value>".
    Logs heart rate (BPM) and oxygen saturation (OXY%) to the database
    under the specified user ID. Displays the values in a formatted table.

    Press 'Esc' to exit logging mode.

    Input:  
        current_user_id (int) - User ID as defined in the database
        username (str)        - Optional username (default: "user")

    Output: 
        None
    *******************************
    """
    print("Entering Bio-Metrics logging mode. Press 'Esc' to exit.")
    exit_flag = threading.Event()
    start_time = datetime.now()

    def uart_listener():
        try:
            ser = serial.Serial(COMPORT, BAUDRATE, timeout=1)
            print(f"Listening on {COMPORT} at {BAUDRATE} baud...")
            print(f"{'User_ID':<8}{'BPM':>8}{'OXY%':>8}{'Time':>10}")
            while not exit_flag.is_set():
                line = ser.readline().decode('utf-8').strip()
                if not line:
                    continue
                try:
                    now = datetime.now()
                    elapsed = int((now - start_time).total_seconds())
                    bpm = None
                    oxygen_level = None
                    if "bpm:" in line and "oxy:" in line:
                        bpm_index = line.find("bpm:")
                        oxy_index = line.find("oxy:")
                        if bpm_index < oxy_index:
                            bpm_part = line[bpm_index:oxy_index].strip()
                            oxy_part = line[oxy_index:].strip()
                        else:
                            oxy_part = line[oxy_index:bpm_index].strip()
                            bpm_part = line[bpm_index:].strip()
                        if bpm_part.startswith("bpm:"):
                            bpm = int(bpm_part.split(":")[1].strip())
                            log_bpm(current_user_id, bpm, now)
                        if oxy_part.startswith("oxy:"):
                            oxygen_level = int(oxy_part.split(":")[1].strip())
                            log_oxygen_level(current_user_id, oxygen_level, now)
                    elif line.startswith("bpm:"):
                        bpm = int(line.split(":")[1].strip())
                        log_bpm(current_user_id, bpm, now)
                    elif line.startswith("oxy:"):
                        oxygen_level = int(line.split(":")[1].strip())
                        log_oxygen_level(current_user_id, oxygen_level, now)

                    if bpm is not None and oxygen_level is not None:
                        print(f"{current_user_id:<8}{bpm:>8}{oxygen_level:>7}%{elapsed:>7}s")
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
            if key == b'\x1b':  # ESC key
                exit_flag.set()

    listener_thread.join()
    print("Exiting Bio-Metrics logging mode.")
