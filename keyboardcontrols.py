import keyboard
import serial
from time import sleep
import threading
import pyglet

robotIsConnected = True
if robotIsConnected: serial = serial.Serial(port='COM5', baudrate = 115200, timeout=.1)
motorSpeedLeft = 0 #Value between 100 and -100
motorSpeedRight = 0 #Value between 100 and -100
data = None
def use_keys():
    global motorSpeedLeft, motorSpeedRight
    if keyboard.is_pressed("m"):
        line = "motor controllerOn\n"
        serial.write(line.encode())

    if keyboard.is_pressed("n"):
        line = "motor controllerOff\n"
        serial.write(line.encode())

    if keyboard.is_pressed("w"):
        motorSpeedLeft = 20
        motorSpeedRight = 20

    if keyboard.is_pressed("s"):
        motorSpeedLeft = -20
        motorSpeedRight = -20

    if keyboard.is_pressed("a"):
        #Turn left
        motorSpeedLeft = 20
        motorSpeedRight = -20

    if keyboard.is_pressed("d"):
        motorSpeedLeft = -20
        motorSpeedRight = 20

    if keyboard.is_pressed("space"):
        motorSpeedLeft = 0
        motorSpeedRight = 0

    if keyboard.is_pressed("p"):
        print("pressed p")
        line = "start\n"
        serial.write(line.encode())

    if keyboard.is_pressed("o"):
        print("pressed o")

        line = "stop\n"
        serial.write(line.encode())

def use_keys_old():
    global motorSpeedLeft, motorSpeedRight
    if keyboard.is_pressed("m"):
        line = "motor controllerOn\n"
        serial.write(line.encode())

    if keyboard.is_pressed("n"):
        line = "motor controllerOff\n"
        serial.write(line.encode())

    if keyboard.is_pressed("w"):
        if motorSpeedLeft >= 100:
            pass
        else:
            motorSpeedLeft += 50

        if motorSpeedRight >= 100:
            pass
        else:
            motorSpeedRight += 50
        
    if keyboard.is_pressed("s"):
        if motorSpeedLeft <= -100:
            pass
        else:
            motorSpeedLeft += -50
        if motorSpeedRight <= -100:
            pass
        else:
            motorSpeedRight += -50

    if keyboard.is_pressed("a"):
        #Turn left
        motorSpeedLeft = 50
        motorSpeedRight = -50

    if keyboard.is_pressed("d"):
        motorSpeedLeft = -50
        motorSpeedRight = 50

    if keyboard.is_pressed("p"):
        print("pressed p")
        line = "start\n"
        serial.write(line.encode())

    if keyboard.is_pressed("o"):
        print("pressed o")

        line = "stop\n"
        serial.write(line.encode())
        
def readSerial():
    global data
    while True:
        data = serial.readline().decode('utf-8').strip()
        print(data)
        sleep(1/50)
    

#serial_monitor_thread = threading.Thread(target = readSerial, daemon = True)

while True:
    use_keys()
    line = f"motor driveLeft {motorSpeedLeft}\nmotor driveRight {motorSpeedRight} \n"
    print(line)

    serial.write(line.encode())

    data = serial.readline().decode('utf-8').strip()
    print(data)
    sleep(1/100)