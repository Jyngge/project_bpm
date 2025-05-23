# *****************************************************************************
# University of Southern Denmark
# Embedded C Programming (ECP)
#
# MODULENAME.: main.py
#
# PROJECT....: PPG pulsefreq. and -oximetry meas.
#
# DESCRIPTION:  
# A simple terminal application for collecting and exporting
# biometric data. This is the entry point of the application.
# It provides a command-line interface for interacting with
# biometric data logging and configuration.
#
# *****************************************************************************

from commands import execute_command, get_available_commands


def main():
    """
    *******************************
    Function: main
    -------------------
    Main entry point for the biometric terminal application.

    Initializes the command-line interface, prints a welcome message,
    and waits for user input in a loop. Delegates command handling
    to the `execute_command` function.

    Input:  None
    Output: None
    *******************************
    """
    print("BPM Terminal App")
    print("Type 'help' to see available commands or 'exit' to quit.")

    while True:
        command = input("> ").strip().lower()
        execute_command(command)


if __name__ == "__main__":
    main()
