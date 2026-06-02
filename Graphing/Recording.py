import argparse
import csv
import re
import threading
import time
from datetime import datetime

import matplotlib.pyplot as plt
import serial
from serial.tools import list_ports


# This pattern looks for the exact line your C++ code prints when you type "print":
# angle=... | pid=... | p=... | i=... | d=... | motor=... | pwmA=... | pwmB=...
VALUE_PATTERN = re.compile(
    r"angle=([-+]?\d*\.?\d+)\s*\|\s*"
    r"pid=([-+]?\d*\.?\d+)\s*\|\s*"
    r"p=([-+]?\d*\.?\d+)\s*\|\s*"
    r"i=([-+]?\d*\.?\d+)\s*\|\s*"
    r"d=([-+]?\d*\.?\d+)\s*\|\s*"
    r"motor=([-+]?\d*\.?\d+)\s*\|\s*"
    r"pwmA=([-+]?\d*\.?\d+)\s*\|\s*"
    r"pwmB=([-+]?\d*\.?\d+)"
)


# These are the columns that will be saved if you type "save".
FIELDS = [
    "time",
    "angle",
    "pid_total",
    "p",
    "i",
    "d",
    "motor_output",
    "pwmA",
    "pwmB",
]


# These variables control the recorder.
recording = False
running = True
start_time = None
samples = []

# This lock stops two Python threads from writing to the robot at the same time.
serial_lock = threading.Lock()


def list_serial_ports():
    # Show all serial ports Python can see, so you can pick the right COM port.
    ports = list(list_ports.comports())

    if not ports:
        print("No serial ports found.")
        return

    print("Available serial ports:")
    for port in ports:
        print(f"  {port.device} - {port.description}")


def parse_values(line):
    # Try to find the angle/PID/motor values inside one serial line.
    match = VALUE_PATTERN.search(line)

    if not match:
        return None

    # Convert all matched text numbers into real float numbers.
    values = [float(value) for value in match.groups()]

    # Give every value a clear name.
    return {
        "angle": values[0],
        "pid_total": values[1],
        "p": values[2],
        "i": values[3],
        "d": values[4],
        "motor_output": values[5],
        "pwmA": values[6],
        "pwmB": values[7],
    }


def serial_reader(ser):
    global start_time

    # This runs constantly in the background.
    # It reads every line coming from the robot.
    while running:
        try:
            raw_line = ser.readline()
        except serial.SerialException as error:
            print(f"\nSerial read error: {error}")
            break

        if not raw_line:
            continue

        # Decode the bytes from serial into normal text.
        line = raw_line.decode(errors="ignore").strip()

        # Print everything from the robot, so you can still see messages/errors.
        if line:
            print(line)

        values = parse_values(line)

        # Only store data when recording is turned on.
        if recording and values is not None:
            now = time.time()

            # The first recorded sample becomes time = 0.
            if start_time is None:
                start_time = now

            row = {
                "time": now - start_time,
                **values,
            }

            samples.append(row)


def print_command_sender(ser, sample_rate):
    # This decides how often Python asks the robot for values.
    # Example: sample_rate = 10 means 10 times per second.
    delay = 1.0 / sample_rate

    while running:
        if recording:
            try:
                # Ask the C++ code to print one set of live values.
                with serial_lock:
                    ser.write(b"print\n")
            except serial.SerialException as error:
                print(f"\nSerial write error: {error}")
                break

        time.sleep(delay)


def save_csv(filename):
    # Save the recorded data to a CSV file.
    # You can open this later in Excel, Google Sheets, or Python.
    if not samples:
        print("No samples recorded, so no CSV was saved.")
        return

    with open(filename, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(samples)

    print(f"Saved CSV: {filename}")


def plot_samples():
    # Make graphs for all recorded values.
    if not samples:
        print("No samples recorded, so no graph was made.")
        return

    times = [row["time"] for row in samples]

    graphs = [
        ("Angle", "angle"),
        ("PID total", "pid_total"),
        ("P", "p"),
        ("I", "i"),
        ("D", "d"),
        ("Motor output", "motor_output"),
        ("pwmA", "pwmA"),
        ("pwmB", "pwmB"),
    ]

    # Create one graph underneath another, all sharing the same time axis.
    fig, axes = plt.subplots(len(graphs), 1, sharex=True, figsize=(12, 14))

    for axis, (title, key) in zip(axes, graphs):
        axis.plot(times, [row[key] for row in samples])
        axis.set_ylabel(title)
        axis.grid(True)

    axes[-1].set_xlabel("Time (seconds)")

    fig.suptitle("Robot values over time")
    fig.tight_layout()

    plt.show()


def handle_user_commands(ser):
    global recording
    global start_time
    global samples
    global running

    # These are commands for the Python recorder.
    print()
    print("Python recorder commands:")
    print("  start recording")
    print("  stop recording")
    print("  clear recording")
    print("  plot")
    print("  save")
    print("  quit")
    print()
    print("Anything else you type is sent to the robot.")
    print("Example robot commands: pid start, pid stop, print, kp 5")
    print()

    while running:
        command = input("> ").strip()

        if command == "start recording":
            # Start a fresh recording.
            samples = []
            start_time = None
            recording = True
            print("Recording started.")

        elif command == "stop recording":
            # Stop recording and immediately show the graphs.
            recording = False
            print(f"Recording stopped. Samples recorded: {len(samples)}")
            plot_samples()

        elif command == "clear recording":
            # Delete the current recorded data.
            samples = []
            start_time = None
            print("Recording cleared.")

        elif command == "plot":
            # Show the graph again without recording new data.
            plot_samples()

        elif command == "save":
            # Save data with a timestamped filename.
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_csv(f"robot_recording_{timestamp}.csv")

        elif command == "quit":
            # Close the Python recorder.
            running = False
            print("Closing recorder.")

        elif command:
            # If it is not a Python command, send it directly to the robot.
            with serial_lock:
                ser.write((command + "\n").encode())


def main():
    # Read optional settings from the terminal command.
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="Serial port, for example COM3")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--sample-rate", type=float, default=10.0)
    args = parser.parse_args()

    # If no COM port was given, show available ports and ask you to choose one.
    if args.port is None:
        list_serial_ports()
        args.port = input("Type the serial port to use, for example COM3: ").strip()

    # Open the serial connection to the robot.
    with serial.Serial(args.port, args.baud, timeout=0.1) as ser:
        print(f"Connected to {args.port} at {args.baud} baud.")

        # Thread 1 reads messages coming from the robot.
        reader_thread = threading.Thread(target=serial_reader, args=(ser,), daemon=True)

        # Thread 2 sends "print" repeatedly while recording is on.
        sender_thread = threading.Thread(
            target=print_command_sender,
            args=(ser, args.sample_rate),
            daemon=True,
        )

        reader_thread.start()
        sender_thread.start()

        # Main thread waits for your typed commands.
        handle_user_commands(ser)


if __name__ == "__main__":
    main()