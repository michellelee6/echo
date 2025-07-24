import smbus2
import time

# TF-Luna I2C default address
TF_LUNA_ADDR = 0x10

# Register to request data from
FRAME_HEADER = 0x5A
REGISTER = 0x00  # Start of frame

# Use I2C bus 1 (default for Pi)
bus = smbus2.SMBus(1)

def read_distance():
    try:
        # Request 9 bytes from sensor
        data = bus.read_i2c_block_data(TF_LUNA_ADDR, REGISTER, 9)

        # Validate frame header
        if data[0] == FRAME_HEADER and data[1] == FRAME_HEADER:
            distance = data[2] + (data[3] << 8)
            strength = data[4] + (data[5] << 8)
            print(f"Distance: {distance} cm | Strength: {strength}")
        else:
            print("Invalid data header:", data)
    except Exception as e:
        print("Error reading from TF-Luna:", e)

while True:
    read_distance()
    time.sleep(0.1)
