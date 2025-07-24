import serial
import time

# Open the serial port (adjust if using different port)
ser = serial.Serial("/dev/ttyAMA0", 115200)

def read_tf_luna():
    while True:
        if ser.in_waiting >= 9:
            data = ser.read(9)
            if data[0] == 0x59 and data[1] == 0x59:
                distance = data[2] + data[3]*256
                strength = data[4] + data[5]*256
                print(f"Distance: {distance} cm, Strength: {strength}")
        time.sleep(0.05)

try:
    read_tf_luna()
except KeyboardInterrupt:
    ser.close()
    print("Stopped.")
