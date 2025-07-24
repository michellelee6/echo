import serial

ser = serial.Serial("/dev/serial0", 115200, timeout=1)

try:
    while True:
        if ser.in_waiting:
            data = ser.read(ser.in_waiting)
            print(" ".join([f"{b:02X}" for b in data]))
except KeyboardInterrupt:
    ser.close()
