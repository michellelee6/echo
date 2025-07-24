import serial
import time

# Open serial port
ser = serial.Serial("/dev/serial0", 115200, timeout=1)

def read_tfluna():
    while True:
        count = ser.in_waiting
        if count >= 9:
            bytes = ser.read(9)
            if bytes[0] == 0x59 and bytes[1] == 0x59:  # frame header
                distance = bytes[2] + bytes[3]*256
                strength = bytes[4] + bytes[5]*256
                print(f"Distance: {distance} cm, Strength: {strength}")
        time.sleep(0.1)

try:
    read_tfluna()
except KeyboardInterrupt:
    ser.close()
