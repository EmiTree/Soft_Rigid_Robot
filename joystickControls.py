"""
    This is a modified version of the example given in the pygame documentation
    https://www.pygame.org/docs/ref/joystick.html
"""

import pygame
import serial
import threading

pygame.init()

# This is a simple class that will help us print to the screen.
# It has nothing to do with the joysticks, just outputting the
# information.
class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 25)

    def tprint(self, screen, text):
        text_bitmap = self.font.render(text, True, (0, 0, 0))
        screen.blit(text_bitmap, (self.x, self.y))
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10
running = True

#Robot state variables to display in the ui
robotConnected = True
robotIsRunning = False
manualControls = False
motorInputLeft = 0
motorInputRight = 0


#Start serial monitor thread
line = None    #Line is the message that is sent to the robot
data = None     #Data is what is read from the serial
if robotConnected: serial = serial.Serial(port='COM5', baudrate = 115200, timeout=.1)

def serial_thread():
    global data, line
    while True:
        if line:
            serial.write(line.encode())
        data = serial.readline().decode('utf-8').strip()
        print(data)
serial_thread = threading.Thread(target = serial_thread, daemon = True)
if robotConnected: serial_thread.start()


def drivingWithStick(xInput, yInput, turning):
    # Get raw joystick inputs
    # yInput is value between -1 and 1 that will map to 20 and -20?
    # Signal is the same for left and right
    # turning is going to be done by having the opposite value to the left and right motors

    scalingFactor = 80

    if not turning:
        speedLeft = int(yInput * scalingFactor)
        speedRight = int(yInput * scalingFactor)
    if turning: # Ik weet nog niet welke het min teken moet krijgen dit moet later aangepast worden
        speedLeft = int(xInput * scalingFactor)
        speedRight = -1 * int(xInput * scalingFactor)

    return speedLeft, speedRight

def drivingForwardsBackwards(yInput):
    # yInput is value between -1 and 1 that will map to 20 and -20?
    # Signal is the same for left and right
    scalingFactor = 20
    speedLeft = int(yInput * scalingFactor)
    speedRight = int(yInput * scalingFactor)  

    return speedLeft, speedRight

def main():
    global running, line, robotIsRunning, robotConnected, manualControls
    # Set the width and height of the screen (width, height), and name the window.
    screen = pygame.display.set_mode((500, 700))
    pygame.display.set_caption("Joystick example")

    # Used to manage how fast the screen updates.
    clock = pygame.time.Clock()

    # Get ready to print.
    text_print = TextPrint()

    # This dict can be left as-is, since pygame will generate a
    # pygame.JOYDEVICEADDED event for every joystick connected
    # at the start of the program.
    joysticks = {}

    while running:
        # Event processing step.
        # Possible joystick events: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
        # JOYBUTTONUP, JOYHATMOTION, JOYDEVICEADDED, JOYDEVICEREMOVED
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # Flag that we are done so we exit this loop.

            if event.type == pygame.JOYBUTTONDOWN:
                print("Joystick button pressed.")
                if event.button == 0:
                    joystick = joysticks[event.instance_id]
                    if joystick.rumble(0, 0.7, 500):
                        print(f"Rumble effect played on joystick {event.instance_id}")
                    line = "start \n" # The A button starts the robot
                    robotIsRunning = True

                if event.button == 1:
                    line = "stop \n" #The B button stops the robot
                    robotIsRunning = False

                if event.button == 2:
                    line = "motor controllerOn\n" # X Button
                    manualControls = True

                if event.button == 3:
                    line = "motor controllerOff\n" # Y Button
                    manualControls = False

            if event.type == pygame.JOYAXISMOTION: # When the joystick is moved update the speed of the motors
                line = f"motor driveLeft {motorInputLeft}\n motor driveRight {motorInputRight}\n"

            if event.type == pygame.JOYBUTTONUP:
                print("Joystick button released.")
                line = None

            # Handle hotplugging
            if event.type == pygame.JOYDEVICEADDED:
                # This event will be generated when the program starts for every
                # joystick, filling up the list without needing to create them manually.
                joy = pygame.joystick.Joystick(event.device_index)
                joysticks[joy.get_instance_id()] = joy
                print(f"Joystick {joy.get_instance_id()} connencted")

            if event.type == pygame.JOYDEVICEREMOVED:
                del joysticks[event.instance_id]
                print(f"Joystick {event.instance_id} disconnected")

        # Drawing step
        # First, clear the screen to white. Don't put other drawing commands
        # above this, or they will be erased with this command.
        screen.fill((255, 255, 255))
        text_print.reset()

        # Get count of joysticks.
        joystick_count = pygame.joystick.get_count()

        text_print.tprint(screen, f"Number of joysticks: {joystick_count}")
        text_print.indent()

        # For each joystick:
        for joystick in joysticks.values():
            jid = joystick.get_instance_id()

            text_print.tprint(screen, f"Joystick {jid}")
            text_print.indent()

            # Get the name from the OS for the controller/joystick.
            name = joystick.get_name()
            text_print.tprint(screen, f"Joystick name: {name}")

            guid = joystick.get_guid()
            text_print.tprint(screen, f"GUID: {guid}")

            power_level = joystick.get_power_level()
            text_print.tprint(screen, f"Joystick's power level: {power_level}")

            # Usually axis run in pairs, up/down for one, and left/right for
            # the other. Triggers count as axes.
            axes = joystick.get_numaxes()
            text_print.tprint(screen, f"Number of axes: {axes}")
            text_print.indent()

            for i in range(axes):
                axis = joystick.get_axis(i)
                text_print.tprint(screen, f"Axis {i} value: {axis:>6.3f}")
            text_print.unindent()

            buttons = joystick.get_numbuttons()
            text_print.tprint(screen, f"Number of buttons: {buttons}")
            text_print.indent()

            for i in range(buttons):
                button = joystick.get_button(i)
                text_print.tprint(screen, f"Button {i:>2} value: {button}")
            text_print.unindent()

            hats = joystick.get_numhats()
            text_print.tprint(screen, f"Number of hats: {hats}")
            text_print.indent()

            # Hat position. All or nothing for direction, not a float like
            # get_axis(). Position is a tuple of int values (x, y).
            for i in range(hats):
                hat = joystick.get_hat(i)
                text_print.tprint(screen, f"Hat {i} value: {str(hat)}")
            text_print.unindent()

            text_print.unindent()

        if abs(joystick.get_axis(0)) <= 0.5: # The robot will only turn if you tilt the joystick far to the left or right
            robotIsTurning = False
        else:
            robotIsTurning = True

        #print(f"joystick {round(joystick.get_axis(0), 2)}, {round(joystick.get_axis(1), 2)}, A: {joystick.get_button(0)}")
        motorInputLeft, motorInputRight = drivingWithStick(joystick.get_axis(0), joystick.get_axis(1), robotIsTurning)

        text_print.tprint(screen, "                 ") # empty row
        text_print.tprint(screen, f"motorInputLeft:{motorInputLeft} motorInputRight:{motorInputRight}")
        text_print.tprint(screen, f"robotIsRunning {robotIsRunning}")
        text_print.tprint(screen, f"manualControls {manualControls}")
        text_print.tprint(screen, f"line: {line}")
        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()
        

        # Limit to 60 frames per second.
        clock.tick(60)



if __name__ == "__main__":
    main()
    robotIsRunning = False
    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    pygame.quit()
    