import keyboard
import serial
from time import sleep

robotIsConnected = True
if robotIsConnected: serial = serial.Serial(port='COM5', baudrate = 115200, timeout=.1)
motorSpeed = 0 #Value between 100 and -100
def use_keys():
    global motorSpeed
    if keyboard.is_pressed("m"):
        line = "motor controllerOn\n"
        serial.write(line.encode())

    if keyboard.is_pressed("n"):
        line = "motor controllerOff\n"
        serial.write(line.encode())

    if keyboard.is_pressed("w"):
        if motorSpeed >= 100:
            pass
        else:
            motorSpeed += 50
        
    if keyboard.is_pressed("s"):
        if motorSpeed <= -100:
            pass
        else:
            motorSpeed += -50

    if keyboard.is_pressed("p"):
        print("pressed p")
        line = "start\n"
        serial.write(line.encode())

    if keyboard.is_pressed("o"):
        print("pressed o")

        line = "stop\n"
        serial.write(line.encode())
        
    
while True:
    use_keys()
    line = f"motor controllerInputLeft {motorSpeed}\n"
    print(line)
    serial.write(line.encode())
    data = serial.readline().decode('utf-8').strip()
    print(data)