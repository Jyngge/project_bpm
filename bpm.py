def add_bio_metrics_entry(user_id, bpm, oxygen_level):
    try:
        cursor = conn.cursor()
        query = "INSERT INTO bpm_log (userID, bpm, oxygen_level, time_stamp) VALUES (%s, %s, %s, %s)"
        timestamp = datetime.now()
        cursor.execute(query, (user_id, bpm, oxygen_level, timestamp))
        conn.commit()
        cursor.close()
        print(f"Bio-metrics entry added for user {user_id}: {bpm} BPM, {oxygen_level}% oxygen at {timestamp}")
    except Exception as e:
        print(f"Error adding bio-metrics entry: {e}")


def get_available_commands():
    # Define the list of available commands
    commands = {
        'add_user': 'Add a new user to the system',
        'remove_user': 'Remove an existing user from the system',
        'set_user': 'Set the current user',
        'show_log': 'Show the BPM log of user',
        'log_bio': 'Log Bio-Metrics data from the COM port',
        'output_to_csv': 'Output the BPM log to a CSV file',
        'set_comport': 'Set the COM port and baudrate for UART communication',
        'help': 'Show available commands',
        'clear': 'Clear the console output',
        'exit': 'Exit the application'
    }
    return commands

def log_bio():
    global current_user, comport, baudrate  # Use the global variables

    if current_user is None:
        print("No user is currently logged in. Please set a user first.")
        return

    print("Entering Bio-Metrics logging mode. Press 'Esc' to exit.")
    
    def uart_listener():
        try:
            # Configure the serial port using the global COM port and baud rate
            ser = serial.Serial(comport, baudrate, timeout=1)
            print(f"Listening for BPM and oxygen data on {comport} at {baudrate} baud...")
            
            while not exit_flag.is_set():
                line = ser.readline().decode('utf-8').strip()
                if line:
                    print(f"Received: {line}")
                    try:
                        # Parse the data format "bpm:<value>,oxy:<value>"
                        data = dict(item.split(":") for item in line.split(","))
                        bpm = int(data.get("bpm", 0))
                        oxygen_level = int(data.get("oxy", 0))
                        
                        # Add the entry to the database
                        add_bio_metrics_entry(current_user, bpm, oxygen_level)
                    except (ValueError, KeyError):
                        print("Invalid data format. Expected 'bpm:<value>,oxy:<value>'.")
        except serial.SerialException as e:
            print(f"Serial error: {e}")
        finally:
            if 'ser' in locals() and ser.is_open:
                ser.close()

    # Thread-safe flag to signal exit
    exit_flag = threading.Event()

    # Start the UART listener in a separate thread
    listener_thread = threading.Thread(target=uart_listener)
    listener_thread.start()

    # Wait for the 'Esc' key press to exit logging mode
    while not exit_flag.is_set():
        if msvcrt.kbhit():  # Check if a key has been pressed
            key = msvcrt.getch()  # Get the pressed key
            if key == b'\x1b':  # ASCII code for 'Esc' key
                print("Exiting Bio-Metrics logging mode.")
                exit_flag.set()

    # Wait for the listener thread to finish
    listener_thread.join()

def set_user():
    global current_user  # Ensure current_user is treated as a global variable
    try:
        username = input("Enter username to set as current user: ").strip()
        cursor = conn.cursor()
        query = "SELECT id FROM user WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            current_user = result[0]  # Update the global variable
            print(f"Current user set to '{username}' (ID: {current_user}).")
        else:
            print(f"User '{username}' not found.")
    except Exception as e:
        print(f"Error setting current user: {e}")

def set_comport():
    global comport, baudrate  # Declare global variables for COM port and baud rate
    try:
        # Prompt the user to enter the COM port and baud rate
        comport = input("Enter the COM port (e.g., COM3): ").strip()
        baudrate = int(input("Enter the baud rate (e.g., 9600): ").strip())
        print(f"COM port set to '{comport}' with baud rate '{baudrate}'.")
    except ValueError:
        print("Invalid baud rate. Please enter a numeric value.")
    except Exception as e:
        print(f"Error setting COM port: {e}")



def output_to_csv():
    try:
        # Get the directory of the executable or script
        if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller executable
            script_dir = os.path.dirname(sys.executable)
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))

        # Prompt the user to enter a username or 'all'
        username = input("Enter the username or 'all' to export all users' logs: ").strip().lower()
        
        if username == "all":
            cursor = conn.cursor()
            query = """
                SELECT user.username, bpm_log.bpm, bpm_log.oxygen_level, bpm_log.time_stamp 
                FROM bpm_log 
                INNER JOIN user ON bpm_log.userID = user.id
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            
            if not rows:
                print("No BPM logs found.")
                return
            
            filename = os.path.join(script_dir, "all_users_bpm_log.csv")
            header = ["Username", "BPM", "Oxygen Level", "Timestamp"]
        else:
            cursor = conn.cursor()
            query = """
                SELECT bpm_log.bpm, bpm_log.oxygen_level, bpm_log.time_stamp 
                FROM bpm_log 
                INNER JOIN user ON bpm_log.userID = user.id 
                WHERE user.username = %s
            """
            cursor.execute(query, (username,))
            rows = cursor.fetchall()
            cursor.close()
            
            if not rows:
                print(f"No BPM log found for user '{username}'.")
                return
            
            filename = os.path.join(script_dir, f"{username}_bpm_log.csv")
            header = ["BPM", "Oxygen Level", "Timestamp"]

        # Write the data to a CSV file
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            
            # Write the header
            writer.writerow(header)
            
            # Write the rows
            writer.writerows(rows)
        
        print(f"BPM log successfully exported to '{filename}'.")
    except Exception as e:
        print(f"Error exporting BPM log to CSV: {e}")

def show_log():
    try:
        # Prompt the user to enter a username or 'all'
        username = input("Enter username to view BPM log or 'all' to view all users' logs: ").strip().lower()

        if username == "all":
            cursor = conn.cursor()
            query = """
                SELECT user.username, bpm_log.bpm, bpm_log.oxygen_level, bpm_log.time_stamp 
                FROM bpm_log 
                INNER JOIN user ON bpm_log.userID = user.id
                ORDER BY user.username, bpm_log.time_stamp
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()

            if rows:
                print("BPM and Oxygen Level log for all users (sorted by username):")
                for username, bpm, oxygen_level, timestamp in rows:
                    print(f"Username: {username}, BPM: {bpm}, Oxygen Level: {oxygen_level}%, Timestamp: {timestamp}")
            else:
                print("No BPM logs found.")
        else:
            cursor = conn.cursor()
            query = """
                SELECT bpm_log.bpm, bpm_log.oxygen_level, bpm_log.time_stamp 
                FROM bpm_log 
                INNER JOIN user ON bpm_log.userID = user.id 
                WHERE user.username = %s
                ORDER BY bpm_log.time_stamp
            """
            cursor.execute(query, (username,))
            rows = cursor.fetchall()
            cursor.close()

            if rows:
                print(f"BPM and Oxygen Level log for user '{username}' (sorted by timestamp):")
                for bpm, oxygen_level, timestamp in rows:
                    print(f"BPM: {bpm}, Oxygen Level: {oxygen_level}%, Timestamp: {timestamp}")
            else:
                print(f"No BPM log found for user '{username}'.")
    except Exception as e:
        print(f"Error fetching BPM log: {e}")

def clear():
    # Clear the terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    print("BPM Terminal App")
    print("Type 'help' to see available commands or 'exit' to quit.")

    while True:
        command = input("> ").strip()
        
        if command.lower() == 'exit':
            print("Exiting the application.")
            break
        elif command.lower() == 'help':
            print("Available commands:")
            for cmd, desc in get_available_commands().items():
                print(f"{cmd}: {desc}")
        elif command.lower() == 'clear':
            clear()
        elif command.lower() == 'add_user':
            try:
                username = input("Enter username: ").strip()
                age = int(input("Enter age: ").strip())
                cursor = conn.cursor()
                query = "INSERT INTO user (username, age) VALUES (%s, %s)"
                cursor.execute(query, (username, age))
                conn.commit()
                cursor.close()
                print(f"User '{username}' added successfully.")
            except Exception as e:
                print(f"Error adding user: {e}")
        elif command.lower() == 'set_user':
            set_user()
        elif command.lower() == 'remove_user':
            try:
                username = input("Enter username to remove: ").strip()
                cursor = conn.cursor()
                query = "DELETE FROM user WHERE username = %s"
                cursor.execute(query, (username,))
                conn.commit()
                cursor.close()
                print(f"User '{username}' removed successfully.")
            except Exception as e:
                print(f"Error removing user: {e}")
        elif command.lower() == 'show_log':
            show_log()
        elif command.lower() == 'log_bio':  # Updated reference
            log_bio()
        elif command.lower() == 'set_comport':
            set_comport()
        elif command.lower() == 'output_to_csv':
            output_to_csv()
        else:
            print(f"Unknown command: {command}. Type 'help' for a list of commands.")

if __name__ == "__main__":
    import os
    import sys
    import serial
    import mysql.connector
    from datetime import datetime
    import threading
    import msvcrt  # For detecting key presses on Windows
    import csv

    # Initialize global variables for COM port and baud rate
    comport = "COM3"  # Default COM port
    baudrate = 9600   # Default baud rate

    # Database connection
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="JkgRWOrUviyGJbjdAX7V",
        database="bio_metric_database"
    )
    current_user = None

    main()

