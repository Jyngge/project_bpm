from commands import execute_command, get_available_commands

def main():
    print("BPM Terminal App")
    print("Type 'help' to see available commands or 'exit' to quit.")

    

    while True:
        command = input("> ").strip().lower()
        execute_command(command)

if __name__ == "__main__":
    main()