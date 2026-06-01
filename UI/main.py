import tkinter as tk
import serial

# Set correct com port for pico
serial = serial.Serial(port='COM12', baudrate = 115200, timeout=.1)

# =============================================================================
# ROBOT CONTROL PANEL
# =============================================================================
# This file is organized into sections so it is easier to understand and change.
#
# The main idea:
# 1. The "state" dictionaries store the current values shown in the window.
# 2. The "settings" lists describe what controls should be created.
# 3. The helper functions update values, labels, and commands.
# 4. The section builder functions create each group of buttons.
# 5. The app setup at the bottom puts everything on screen.
#
# If you want to add a new setting later, you usually only need to add one item
# to one of the configuration lists below.

DARK_BG = "#1e1e1e"
DARK_PANEL = "#2b2b2b"
DARK_TEXT = "#f0f0f0"
DARK_BUTTON = "#3a3a3a"
DARK_BUTTON_ACTIVE = "#505050"




# =============================================================================
# CURRENT ROBOT VALUES
# =============================================================================

pid_values = {
    "Kp": 20.0,
    "Ki": 0.0,
    "Kd": 0.05,
}

servo_positions = {
    1: 0,
    2: 0,
    3: 0,
    4: 0,
}

motor_values = {
    "max_pwm": 80,
    "motor_start_pwm": 20,
    "pid_output_limit": 60,
}

status_label = None


control_values = {
    "deadband_value": 5,
    "response_curve_value": 2,
}

SPECIFIC_SERVO_DIRECTIONS = ["forward", "backward", "left", "right"]

SPECIFIC_SERVO_ACTIONS = [
    "curve",
    "lean",
    "tense",
    "floppy",
]



# =============================================================================
# UI CONFIGURATION
# =============================================================================

PID_SETTINGS = [
    {"name": "Kp", "steps": [0.01, 0.1], "decimal_places": 4, "command_name": "kp"},
    {"name": "Ki", "steps": [0.01, 0.1], "decimal_places": 4, "command_name": "ki"},
    {"name": "Kd", "steps": [0.01, 0.1], "decimal_places": 4, "command_name": "kd"},
]

SERVO_SETTINGS = [
    {"servo_number": 1, "speed": 40, "time": 0.5},
    {"servo_number": 2, "speed": 40, "time": 0.5},
    {"servo_number": 3, "speed": 40, "time": 0.5},
    {"servo_number": 4, "speed": 40, "time": 0.5},
]

MOTOR_SETTINGS = [
    {
        "name": "max_pwm",
        "display_name": "Max PWM",
        "step": 1,
        "minimum": 0,
        "maximum": 100,
        "command": "motor maxpwm",
    },
    {
        "name": "motor_start_pwm",
        "display_name": "Motor Start PWM",
        "step": 1,
        "minimum": 0,
        "maximum": "max_pwm",
        "command": "motor startpwm",
    },
    {
        "name": "pid_output_limit",
        "display_name": "PID Output Limit",
        "step": 1,
        "minimum": 1,
        "maximum": 1000,
        "command": "motor pidlimit",
    },
]

GENERAL_COMMANDS = [
    {"button_text": "Start PID", "command": "pid start"},
    {"button_text": "Stop PID", "command": "pid stop"},
    {"button_text": "FORCE STOP", "command": "FORCE"},
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def style_widget(widget):
    """Apply dark mode colors to one widget."""
    widget_type = widget.winfo_class()

    if widget_type in ["Frame", "Labelframe"]:
        widget.config(bg=DARK_BG)

    elif widget_type == "Label":
        widget.config(bg=DARK_BG, fg=DARK_TEXT)

    elif widget_type == "Button":
        widget.config(
            bg=DARK_BUTTON,
            fg=DARK_TEXT,
            activebackground=DARK_BUTTON_ACTIVE,
            activeforeground=DARK_TEXT,
            relief="raised",
        )

    elif widget_type == "Canvas":
        widget.config(bg=DARK_BG)

    # LabelFrame titles are controlled through child label styling,
    # so we style children below too.
    for child in widget.winfo_children():
        style_widget(child)


def apply_dark_mode(window):
    """Apply dark mode to the whole app."""
    window.config(bg=DARK_BG)
    style_widget(window)

def send_to_pico(command):
    """Send a command to the Raspberry Pi Pico."""
    print("Sending:", command)
    #Checkpoint                             # Should you check if serial is available
    #                                         Add endline to command. 
    serial.write(f"{command}\n".encode()) #        I have no clue how the command is formatted to i assume it needs to be encoded to utf-8 / ascii
    
    if status_label is not None:
        status_label.config(text=f"Last command sent: {command}")


def clamp(value, minimum, maximum):
    """Keep a number between a minimum and maximum value."""
    return max(minimum, min(maximum, value))

def get_motor_limit(limit):
    """Return a motor limit value."""
    if isinstance(limit, str):
        return motor_values[limit]

    return limit

def update_label(label, display_name, value):
    """Update a label so the screen shows the latest value."""
    label.config(text=f"{display_name}: {value}")

def move_continuous_servo(servo_number, direction, speed, move_time):
    send_to_pico(f"servo {servo_number} {direction} {speed} {move_time}")

    movement_amount = speed * move_time

    if direction == "forward":
        servo_positions[servo_number] += movement_amount
    elif direction == "reverse":
        servo_positions[servo_number] -= movement_amount

    servo_positions[servo_number] = round(servo_positions[servo_number], 2)
        
def zero_continuous_servo(servo_number, speed):
    position = servo_positions[servo_number]

    if position > 0:
        direction = "reverse"
    elif position < 0:
        direction = "forward"
    else:
        return

    move_time = abs(position) / speed
    send_to_pico(f"servo {servo_number} {direction} {speed} {move_time}")

    servo_positions[servo_number] = 0
    
    
def change_control_value(name, amount, label, minimum, maximum, command_name):
    """Change a control setting value and send it to the Pico."""
    control_values[name] = clamp(control_values[name] + amount, minimum, maximum)

    label.config(text=f"{name}: {control_values[name]}")
    send_to_pico(f"{command_name} {control_values[name]}")


def set_deadband(enabled):
    """Turn deadband on or off."""
    if enabled:
        send_to_pico("deadband on")
    else:
        send_to_pico("deadband off")


def set_response_curve(enabled):
    """Turn response curve on or off."""
    if enabled:
        send_to_pico("curve on")
    else:
        send_to_pico("curve off")



def send_specific_servo_command(direction, action):
    """Send a preset tentacle/servo movement command.

    Examples:
    specific forward curve
    specific left lean
    specific right tense

    Your Pico code can read these commands and decide how each servo should move.
    """
    send_to_pico(f"specific {direction} {action}")
    
def send_specific_servo_command(direction, action):
    send_to_pico(f"specific {direction} {action}")

# =============================================================================
# VALUE CHANGE FUNCTIONS
# =============================================================================

def change_pid(setting, amount, label):
    """Change one PID value by a small amount."""
    name = setting["name"]
    decimal_places = setting["decimal_places"]
    command_name = setting["command_name"]

    pid_values[name] = round(pid_values[name] + amount, decimal_places)

    update_label(label, name, pid_values[name])
    send_to_pico(f"{command_name} {pid_values[name]}")


def change_servo_speed(setting, amount, label):
    """Change the speed used by one continuous servo."""
    setting["speed"] = clamp(setting["speed"] + amount, 0, 100)
    label.config(text=f"Speed: {setting['speed']}")


def change_servo_time(setting, amount, label):
    """Change how long one continuous servo should move."""
    setting["time"] = round(clamp(setting["time"] + amount, 0.1, 10), 2)
    label.config(text=f"Time: {setting['time']} seconds")


def update_servo_position_label(label, servo_number):
    """Update the estimated position label for one servo."""
    label.config(text=f"Servo {servo_number} estimated position: {servo_positions[servo_number]}")

def change_motor_setting(setting, amount, label):
    """Change one motor setting by a small amount."""
    name = setting["name"]
    display_name = setting["display_name"]
    minimum = get_motor_limit(setting["minimum"])
    maximum = get_motor_limit(setting["maximum"])

    motor_values[name] = clamp(motor_values[name] + amount, minimum, maximum)

    update_label(label, display_name, motor_values[name])
    send_to_pico(f"{setting['command']} {motor_values[name]}")
    
def reset_all_servo_settings(servo_labels):
    """Set every servo's speed and time to 0.

    This is useful when you want to make sure no servo will move
    before pressing one of the big movement buttons.
    """
    for setting in SERVO_SETTINGS:
        setting["speed"] = 0
        setting["time"] = 0

        servo_number = setting["servo_number"]
        update_servo_setting_label(servo_labels[servo_number], setting)

def update_servo_setting_label(label, setting):
    """Update the label that shows one servo's speed and time."""
    label.config(
        text=(
            f"Servo {setting['servo_number']} | "
            f"Speed: {setting['speed']} | "
            f"Time: {setting['time']}s | "
            f"Estimated position: {servo_positions[setting['servo_number']]}"
        )
    )

def change_servo_speed(setting, amount, label):
    """Change one servo's speed setting."""
    setting["speed"] = clamp(setting["speed"] + amount, -100, 100)
    update_servo_setting_label(label, setting)

def change_servo_time(setting, amount, label):
    """Change one servo's movement time setting."""
    setting["time"] = round(clamp(setting["time"] + amount, 0, 10), 2)
    update_servo_setting_label(label, setting)

def move_all_servos(servo_labels):
    """Move every servo using its own speed and time settings.

    Positive speed moves forward.
    Negative speed moves reverse.
    Speed 0 or time 0 means that servo will not move.
    """
    for setting in SERVO_SETTINGS:
        servo_number = setting["servo_number"]
        speed = setting["speed"]
        move_time = setting["time"]

        if speed == 0 or move_time == 0:
            continue

        if speed > 0:
            direction = "forward"
        else:
            direction = "reverse"

        move_continuous_servo(
            servo_number,
            direction,
            abs(speed),
            move_time,
        )

        update_servo_setting_label(servo_labels[servo_number], setting)

def zero_all_servos(servo_labels):
    """Move all servos back toward their estimated zero position."""
    for setting in SERVO_SETTINGS:
        servo_number = setting["servo_number"]
        speed = setting["speed"]

        if speed == 0:
            continue

        zero_continuous_servo(servo_number, speed)
        update_servo_setting_label(servo_labels[servo_number], setting)


# =============================================================================
# UI BUILDING FUNCTIONS
# =============================================================================

def create_section(parent, title, row, column):
    """Create a labeled section inside the main grid."""
    section = tk.LabelFrame(
        parent,
        text=title,
        padx=10,
        pady=10,
        bg=DARK_BG,
        fg=DARK_TEXT,
    )
    section.grid(row=row, column=column, sticky="nsew", padx=5, pady=5)
    return section

def create_adjustment_buttons(parent, minus_text, plus_text, minus_command, plus_command, width):
    """Create a pair of minus and plus buttons."""
    tk.Button(parent, text=minus_text, width=width, command=minus_command).pack(pady=1)
    tk.Button(parent, text=plus_text, width=width, command=plus_command).pack(pady=1)

def build_pid_section(parent):
    """Create all PID controls."""
    for setting in PID_SETTINGS:
        name = setting["name"]

        label = tk.Label(parent, text=f"{name}: {pid_values[name]}")
        label.pack(pady=(8, 2))

        for step in setting["steps"]:
            create_adjustment_buttons(
                parent=parent,
                minus_text=f"-{step}",
                plus_text=f"+{step}",
                minus_command=lambda s=setting, l=label, amount=step: change_pid(s, -amount, l),
                plus_command=lambda s=setting, l=label, amount=step: change_pid(s, amount, l),
                width=18,
            )

def build_servo_section(parent):
    """Create continuous servo controls in a 2x2 grid."""

    servo_labels = {}

    # This frame holds the 4 servo boxes.
    servo_grid = tk.Frame(parent)
    servo_grid.pack(fill="both", expand=True)

    for index, setting in enumerate(SERVO_SETTINGS):
        servo_number = setting["servo_number"]

        # index 0 -> row 0, column 0
        # index 1 -> row 0, column 1
        # index 2 -> row 1, column 0
        # index 3 -> row 1, column 1
        row = index // 2
        column = index % 2

        servo_box = tk.LabelFrame(
            servo_grid,
            text=f"Servo {servo_number}",
            padx=8,
            pady=8,
        )
        servo_box.grid(row=row, column=column, sticky="nsew", padx=5, pady=5)

        servo_grid.columnconfigure(column, weight=1)

        label = tk.Label(servo_box)
        label.pack(pady=(0, 4))

        servo_labels[servo_number] = label
        update_servo_setting_label(label, setting)

        speed_step = 1
        time_step = 0.1

        create_adjustment_buttons(
            parent=servo_box,
            minus_text=f"-{speed_step}",
            plus_text=f"+{speed_step}",
            minus_command=lambda s=setting, l=label, amount=speed_step: change_servo_speed(s, -amount, l),
            plus_command=lambda s=setting, l=label, amount=speed_step: change_servo_speed(s, amount, l),
            width=10,
        )

        create_adjustment_buttons(
            parent=servo_box,
            minus_text=f"-{time_step}",
            plus_text=f"+{time_step}",
            minus_command=lambda s=setting, l=label, amount=time_step: change_servo_time(s, -amount, l),
            plus_command=lambda s=setting, l=label, amount=time_step: change_servo_time(s, amount, l),
            width=10,
        )

    button_frame = tk.Frame(parent)
    button_frame.pack(fill="x", pady=(10, 0))

    tk.Button(
        button_frame,
        text="GO",
        width=12,
        command=lambda: move_all_servos(servo_labels),
    ).pack(side="left", padx=3)

    tk.Button(
        button_frame,
        text="GO ZERO",
        width=12,
        command=lambda: zero_all_servos(servo_labels),
    ).pack(side="left", padx=3)

    tk.Button(
        button_frame,
        text="SET ALL 0",
        width=12,
        command=lambda: reset_all_servo_settings(servo_labels),
    ).pack(side="left", padx=3)
    
def build_motor_section(parent):
    """Create all motor controls."""
    for setting in MOTOR_SETTINGS:
        name = setting["name"]
        display_name = setting["display_name"]

        label = tk.Label(parent, text=f"{display_name}: {motor_values[name]}")
        label.pack(pady=(8, 2))

        create_adjustment_buttons(
            parent=parent,
            minus_text=f"- {display_name}",
            plus_text=f"+ {display_name}",
            minus_command=lambda s=setting, l=label: change_motor_setting(s, -s["step"], l),
            plus_command=lambda s=setting, l=label: change_motor_setting(s, s["step"], l),
            width=22,
        )

def build_general_section(parent):
    """Create the general command buttons."""
    for command_info in GENERAL_COMMANDS:
        tk.Button(
            parent,
            text=command_info["button_text"],
            width=15,
            command=lambda c=command_info["command"]: send_to_pico(c),
        ).pack(side="left", padx=5)

def build_control_settings_section(parent):
    """Create deadband and response curve controls."""

    deadband_label = tk.Label(
        parent,
        text=f"deadband_value: {control_values['deadband_value']}",
    )
    deadband_label.pack(pady=(8, 2))

    tk.Button(
        parent,
        text="Deadband ON",
        width=18,
        command=lambda: set_deadband(True),
    ).pack(pady=1)

    tk.Button(
        parent,
        text="Deadband OFF",
        width=18,
        command=lambda: set_deadband(False),
    ).pack(pady=1)

    create_adjustment_buttons(
        parent=parent,
        minus_text="-1",
        plus_text="+1",
        minus_command=lambda: change_control_value(
            "deadband_value",
            -1,
            deadband_label,
            0,
            100,
            "deadband value",
        ),
        plus_command=lambda: change_control_value(
            "deadband_value",
            1,
            deadband_label,
            0,
            100,
            "deadband value",
        ),
        width=18,
    )

    response_curve_label = tk.Label(
        parent,
        text=f"response_curve_value: {control_values['response_curve_value']}",
    )
    response_curve_label.pack(pady=(12, 2))

    tk.Button(
        parent,
        text="Response Curve ON",
        width=18,
        command=lambda: set_response_curve(True),
    ).pack(pady=1)

    tk.Button(
        parent,
        text="Response Curve OFF",
        width=18,
        command=lambda: set_response_curve(False),
    ).pack(pady=1)

    create_adjustment_buttons(
        parent=parent,
        minus_text="-1",
        plus_text="+1",
        minus_command=lambda: change_control_value(
            "response_curve_value",
            -1,
            response_curve_label,
            0,
            100,
            "curve value",
        ),
        plus_command=lambda: change_control_value(
            "response_curve_value",
            1,
            response_curve_label,
            0,
            100,
            "curve value",
        ),
        width=18,
    )
    
def build_specific_servo_settings_section(parent):
    """Create preset buttons for specific tentacle movements.

    Rows are directions: forward, backward, left, right.
    Columns are actions: curve, lean, tense, floppy.
    """

    for column, action in enumerate(SPECIFIC_SERVO_ACTIONS):
        header = tk.Label(parent, text=action.title())
        header.grid(row=0, column=column + 1, padx=4, pady=4)

    for row, direction in enumerate(SPECIFIC_SERVO_DIRECTIONS):
        direction_label = tk.Label(parent, text=direction.title())
        direction_label.grid(row=row + 1, column=0, padx=4, pady=4, sticky="e")

        for column, action in enumerate(SPECIFIC_SERVO_ACTIONS):
            tk.Button(
                parent,
                text=action.title(),
                width=10,
                command=lambda d=direction, a=action: send_specific_servo_command(d, a),
            ).grid(row=row + 1, column=column + 1, padx=3, pady=3)
            
# =============================================================================
# APP SETUP
# =============================================================================

def create_scrollable_area(parent):
    """Create a scrollable area for the main controls.

    This helps when the UI gets too tall for the screen.
    The PID, servo, and motor sections will go inside this scrollable frame.
    """
    canvas = tk.Canvas(parent, highlightthickness=0)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)

    scrollable_frame = tk.Frame(canvas)

    canvas_window = canvas.create_window(
        (0, 0),
        window=scrollable_frame,
        anchor="nw",
    )

    def update_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def update_frame_width(event):
        canvas.itemconfig(canvas_window, width=event.width)

    scrollable_frame.bind("<Configure>", update_scroll_region)
    canvas.bind("<Configure>", update_frame_width)

    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return scrollable_frame

def create_app():
    """Create and return the main Tkinter window."""
    global status_label

    window = tk.Tk()
    window.title("Robot Control Panel")

    # Get your screen size.
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Make the window almost the full screen.
    # The -80 and -120 leave room for the taskbar/window borders.
    window_width = screen_width - 80
    window_height = screen_height - 120

    window.geometry(f"{window_width}x{window_height}+20+20")

    title_label = tk.Label(
        window,
        text="Robot Control Panel",
        font=("Arial", 18, "bold"),
    )
    title_label.pack(pady=(10, 0))

    # This outer frame holds the scrollable area.
    scroll_area_container = tk.Frame(window)
    scroll_area_container.pack(fill="both", expand=True, padx=10, pady=10)

    # Anything placed inside main_frame can scroll if it gets too tall.
    main_frame = create_scrollable_area(scroll_area_container)

    for column in range(4):
        main_frame.columnconfigure(column, weight=1)

    pid_frame = create_section(main_frame, "PID Settings", row=0, column=0)
    servo_frame = create_section(main_frame, "Servo Control", row=0, column=1)
    motor_frame = create_section(main_frame, "Motor Settings", row=0, column=2)
    control_frame = create_section(main_frame, "Control Settings", row=0, column=3)
    build_control_settings_section(control_frame)
    
    specific_servo_frame = tk.LabelFrame(
        main_frame,
        text="Specific Servo Settings",
        padx=10,
        pady=10,
        bg=DARK_BG,
        fg=DARK_TEXT,
    )

    specific_servo_frame.grid(
        row=1,
        column=0,
        columnspan=4,
        sticky="nsew",
        padx=5,
        pady=5,
    )

    build_specific_servo_settings_section(specific_servo_frame)
    build_pid_section(pid_frame)
    build_servo_section(servo_frame)
    build_motor_section(motor_frame)

    general_frame = tk.LabelFrame(window, text="General", padx=10, pady=10, bg=DARK_BG, fg=DARK_TEXT)
    general_frame.pack(fill="x", padx=10, pady=5)
    build_general_section(general_frame)

    status_label = tk.Label(
        window,
        text="Last command sent: none yet",
        anchor="w",
        padx=10,
    )
    status_label.pack(fill="x", padx=10, pady=(0, 10))

    apply_dark_mode(window)
    return window
# =============================================================================
# START THE PROGRAM
# =============================================================================

if __name__ == "__main__":
    app = create_app()
    app.mainloop()