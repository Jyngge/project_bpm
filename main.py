# *****************************************************************************
# University of Southern Denmark
# Embedded C Programming (ECP)
#
# MODULENAME.: main.py
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

from commands import execute_command, get_available_commands

def main():
    print("BPM Terminal App")
    print("Type 'help' to see available commands or 'exit' to quit.")

    while True:
        command = input("> ").strip().lower()
        execute_command(command)

if __name__ == "__main__":
    main()