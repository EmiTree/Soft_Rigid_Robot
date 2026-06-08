import csv
import serial
import time

ser = serial.Serial('COM3', 115200)  # Adjust baud rate if needed
setpoint = -5.5 #change set point after every balancing change
start_time = time.time()
bent = False
with open("TestvaluesbendingLeft08_3.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)

    while time.time() - start_time < 10:  # Run for 10 seconds
        print(round(time.time() - start_time, 2))

        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()

            if data.startswith("A"):
                angle = float(data[1:]) + setpoint  # Remove the "A%" prefix and convert to float 

                if (time.time() - start_time >= 5) and not bent: 
                        print("Bleep bloop")
                        if serial.available():
                            serial.write("servo CurveLeft\n".encode())  # Send command to servo
                            bent = True
                writer.writerow([
                    time.time() - start_time,
                    angle
                ])
print("Finished recording.")
ser.close()