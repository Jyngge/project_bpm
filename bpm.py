start_time = None  # To track the time of the first entry

def add_bpm_entry(user_id, bpm):
    global start_time
    try:
        cursor = conn.cursor()
        query = "INSERT INTO bpm_table (userID, bpm, time_stamp) VALUES (%s, %s, %s)"
        current_time = datetime.now()
        
        # Set the start_time if it's the first entry
        if start_time is None:
            start_time = current_time
        
        # Calculate elapsed time in seconds
        elapsed_time = (current_time - start_time).total_seconds()
        
        # Log the entry to the database
        cursor.execute(query, (user_id, bpm, current_time.time()))
        conn.commit()
        cursor.close()
        
        # Print the formatted output
        print(f"ID: {user_id:<3} BPM: {bpm:>3} Time: {elapsed_time:.2f} seconds")
    except Exception as e:
        print(f"Error adding BPM entry: {e}")


def add_oxygen_level_entry(user_id, oxygen_level):
    global start_time
    try:
        cursor = conn.cursor()
        query = "INSERT INTO oxygen_level_table (userID, oxygen_level, time_stamp) VALUES (%s, %s, %s)"
        current_time = datetime.now()
        
        # Set the start_time if it's the first entry
        if start_time is None:
            start_time = current_time
        
        # Calculate elapsed time in seconds
        elapsed_time = (current_time - start_time).total_seconds()
        
        # Log the entry to the database
        cursor.execute(query, (user_id, oxygen_level, current_time.time()))
        conn.commit()
        cursor.close()
        
        # Print the formatted output
        print(f"ID: {user_id:<3} OXY: {oxygen_level:>3} Time: {elapsed_time:.2f} seconds")
    except Exception as e:
        print(f"Error adding oxygen level entry: {e}")


def add_bio_metrics_entry(user_id, bpm, oxygen_level):
    try:
        cursor = conn.cursor()
        query = "INSERT INTO bpm_log (userID, bpm, oxygen_level, time_stamp) VALUES (%s, %s, %s, %s)"
        timestamp = datetime.now().time()  # Use .time() to get only the time
        cursor.execute(query, (user_id, bpm, oxygen_level, timestamp))
        conn.commit()
        cursor.close()
        print(f"Bio-metrics entry added for user {user_id}: {bpm} BPM, {oxygen_level}% oxygen at {timestamp}")
    except Exception as e:
        print(f"Error adding bio-metrics entry: {e}")


def get_available_commands():

    commands = {
        'add_user': 'Add a new user to the system',
        'remove_user': 'Remove an existing user from the system',
        'set_user': 'Set the current user',
        'show_bpm_log': 'Show the BPM log of users',
        'show_oxygen_log': 'Show the oxygen level log of users',
        'log_bio': 'Log Bio-Metrics data from the COM port',
        'output_to_csv': 'Output the BPM and oxygen logs to a CSV file',
        'set_comport': 'Set the COM port and baudrate for UART communication',
        'delete_logs': 'Delete logs for a specific user or all users',  # New command
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
            print(f"Listening for data on {comport} at {baudrate} baud...")
            
            while not exit_flag.is_set():
                line = ser.readline().decode('utf-8').strip()
                if line:
                    
                    try:
                        # Split the line into parts if both bpm and oxy are present
                        if "bpm:" in line and "oxy:" in line:
                            # Ensure the order of bpm and oxy doesn't matter
                            bpm_index = line.find("bpm:")
                            oxy_index = line.find("oxy:")
                            
                            if bpm_index < oxy_index:
                                bpm_part = line[bpm_index:oxy_index].strip()
                                oxy_part = line[oxy_index:].strip()
                            else:
                                oxy_part = line[oxy_index:bpm_index].strip()
                                bpm_part = line[bpm_index:].strip()
                            
                            # Process bpm
                            if bpm_part.startswith("bpm:"):
                                bpm = int(bpm_part.split(":")[1].strip())
                                add_bpm_entry(current_user, bpm)
                            
                            # Process oxygen level
                            if oxy_part.startswith("oxy:"):
                                oxygen_level = int(oxy_part.split(":")[1].strip())
                                add_oxygen_level_entry(current_user, oxygen_level)
                        
                        # Handle cases where only bpm is present
                        elif line.startswith("bpm:"):
                            bpm = int(line.split(":")[1].strip())
                            add_bpm_entry(current_user, bpm)
                        
                        # Handle cases where only oxygen level is present
                        elif line.startswith("oxy:"):
                            oxygen_level = int(line.split(":")[1].strip())
                            add_oxygen_level_entry(current_user, oxygen_level)
                        
                        else:
                            print("Invalid data format. Expected 'bpm:<value>', 'oxy:<value>', or both.")
                    except (ValueError, IndexError):
                        print("Error parsing data. Ensure the format is correct.")
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

        # Prompt the user to choose the type of data to export
        data_type = input("Enter 'bpm' to export BPM logs, 'oxygen' to export oxygen level logs, or 'all' to export both: ").strip().lower()

        if data_type not in ['bpm', 'oxygen', 'all']:
            print("Invalid option. Please enter 'bpm', 'oxygen', or 'all'.")
            return

        # Prompt the user to enter a username or 'all'
        username = input("Enter the username or 'all' to export logs: ").strip().lower()

        if data_type in ['bpm', 'all']:
            # Export BPM logs
            if username == "all":
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
            # Export oxygen level logs
            if username == "all":
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


def show_bpm_log():
    try:
        # Prompt the user to enter a username or 'all'
        username = input("Enter username to view BPM logs or 'all' to view all users' BPM logs: ").strip().lower()

        if username == "all":
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

            if rows:
                print("BPM log for all users (sorted by username):")
                for username, bpm, timestamp in rows:
                    print(f"Username: {username}, BPM: {bpm}, Timestamp: {timestamp}")
            else:
                print("No BPM logs found.")
        else:
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

            if rows:
                print(f"BPM log for user '{username}' (sorted by timestamp):")
                for bpm, timestamp in rows:
                    print(f"BPM: {bpm}, Timestamp: {timestamp}")
            else:
                print(f"No BPM log found for user '{username}'.")
    except Exception as e:
        print(f"Error fetching BPM logs: {e}")

def show_oxygen_log():
    try:
        # Prompt the user to enter a username or 'all'
        username = input("Enter username to view oxygen level logs or 'all' to view all users' oxygen level logs: ").strip().lower()

        if username == "all":
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

            if rows:
                print("Oxygen level log for all users (sorted by username):")
                for username, oxygen_level, timestamp in rows:
                    print(f"Username: {username}, Oxygen Level: {oxygen_level}%, Timestamp: {timestamp}")
            else:
                print("No oxygen level logs found.")
        else:
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

            if rows:
                print(f"Oxygen level log for user '{username}' (sorted by timestamp):")
                for oxygen_level, timestamp in rows:
                    print(f"Oxygen Level: {oxygen_level}%, Timestamp: {timestamp}")
            else:
                print(f"No oxygen level log found for user '{username}'.")
    except Exception as e:
        print(f"Error fetching oxygen level logs: {e}")

def delete_logs():
    try:
        # Prompt the user to enter a username or 'all'
        username = input("Enter the username to delete logs for, or 'all' to delete logs for all users: ").strip().lower()

        if username == "all":
            # Delete logs for all users
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bpm_table")
            cursor.execute("DELETE FROM oxygen_level_table")
            conn.commit()
            cursor.close()
            print("All logs have been deleted.")
        else:
            # Delete logs for a specific user
            cursor = conn.cursor()
            query = "SELECT id FROM user WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            if result:
                user_id = result[0]
                cursor.execute("DELETE FROM bpm_table WHERE userID = %s", (user_id,))
                cursor.execute("DELETE FROM oxygen_level_table WHERE userID = %s", (user_id,))
                conn.commit()
                cursor.close()
                print(f"Logs for user '{username}' have been deleted.")
            else:
                print(f"User '{username}' not found.")
    except Exception as e:
        print(f"Error deleting logs: {e}")

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
        elif command.lower() == 'show_bpm_log':
            show_bpm_log()
        elif command.lower() == 'show_oxygen_log':
            show_oxygen_log()
        elif command.lower() == 'log_bio':
            log_bio()
        elif command.lower() == 'set_comport':
            set_comport()
        elif command.lower() == 'output_to_csv':
            output_to_csv()
        elif command.lower() == 'delete_logs':
            delete_logs()
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
    comport = "COM5"  # Default COM port
    baudrate = 115200   # Default baud rate

    # Database connection
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="JkgRWOrUviyGJbjdAX7V",
        database="bio_metric_database"
    )
    current_user = 7   # Default user ID (can be set to None if no user is logged in)

    main()

