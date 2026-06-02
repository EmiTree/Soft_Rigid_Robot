import argparse
import csv
import re
import threading
import time
from datetime import datetime

import matplotlib.pyplot as plt
import serial
from serial.tools import list_ports

auto_print_lines_to_hide = 0

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
# This pattern looks for lines like "PARAM_CHANGE,paramName,oldValue,newValue" that your C++ code prints when you change a parameter.
PARAM_CHANGE_PATTERN = re.compile(
    r"PARAM_CHANGE,([^,]+),([^,]+),([^,]+)"
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
parameter_changes = []
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
    global auto_print_lines_to_hide

    while running:
        try:
            raw_line = ser.readline()
        except serial.SerialException as error:
            print(f"\nSerial read error: {error}")
            break

        if not raw_line:
            continue

        line = raw_line.decode(errors="ignore").strip()
        change_match = PARAM_CHANGE_PATTERN.search(line)

        if change_match:

            if recording and start_time is not None:

                parameter_changes.append({
                    "time": time.time() - start_time,
                    "parameter": change_match.group(1),
                    "old": float(change_match.group(2)),
                    "new": float(change_match.group(3)),
                })

            continue
        values = parse_values(line)

        if recording and values is not None:
            now = time.time()

            if start_time is None:
                start_time = now

            samples.append({
                "time": now - start_time,
                **values,
            })

            continue

        # Hide the extra lines caused by Python automatically sending "print".
        if recording and auto_print_lines_to_hide > 0:
            auto_print_lines_to_hide -= 1
            continue

        # Only show normal robot messages.
        if line and values is None:
            print(f"\n{line}")

def print_command_sender(ser, sample_rate):
    global auto_print_lines_to_hide

    delay = 1.0 / sample_rate

    while running:
        if recording:
            try:
                with serial_lock:
                    # Your C++ "print" command sends several lines.
                    # We hide those automatic lines so the terminal stays usable.
                    auto_print_lines_to_hide += 8
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
        ("Angle", "angle", "tab:blue"),
        ("PID total", "pid_total", "tab:orange"),
        ("P", "p", "tab:green"),
        ("I", "i", "tab:red"),
        ("D", "d", "tab:purple"),
        ("Motor output", "motor_output", "tab:brown"),
        ("pwmA", "pwmA", "tab:pink"),
        ("pwmB", "pwmB", "tab:cyan"),
    ]

    # Create a 4x2 grid: 4 rows and 2 columns.
    fig, axes = plt.subplots(4, 2, figsize=(14, 10), sharex=True)

    # Flatten turns the 4x2 axes grid into one simple list,
    # so we can loop over it easily.
    axes = axes.flatten()

    for axis, (title, key, color) in zip(axes, graphs):
        axis.plot(times, [row[key] for row in samples], color=color)
        axis.set_title(title)
        axis.set_xlabel("Time (seconds)")
        axis.set_ylabel(title)
        axis.grid(True)
        for change in parameter_changes:

            axis.axvline(
                change["time"],
                linestyle="--",
                alpha=0.4
            )

            ymax = axis.get_ylim()[1]

            axis.text(
                change["time"],
                ymax,
                f'{change["parameter"]}\n'
                f'{change["old"]:.2f}->{change["new"]:.2f}',
                rotation=90,
                fontsize=6,
                verticalalignment="top"
            )

    fig.suptitle("Robot values over time")
    fig.tight_layout()

    plt.show(block=False)
    plt.pause(0.1)
    
def handle_user_commands(ser):
    global recording
    global start_time
    global samples
    global running
    global parameter_changes
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
            samples = []
            parameter_changes = []  
            start_time = None
            recording = True
            print("Recording started.")


        elif command == "stop recording":
            recording = False
            print(f"Recording stopped. Samples recorded: {len(samples)}")
            plot_samples()

        elif command == "clear recording":
            samples = []
            start_time = None
            print("Recording cleared.")

        elif command == "plot":
            plot_samples()

        elif command == "save":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_csv(f"robot_recording_{timestamp}.csv")

        elif command == "quit":
            running = False
            print("Closing recorder.")

        elif command:
            with serial_lock:
                ser.write((command + "\n").encode())
    
def main():
    # Read optional settings from the terminal command.
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default="COM10", help="Serial port, for example COM10")
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