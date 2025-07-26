import smbus2
import time

# TF-Luna I2C addresses
SENSOR_ADDRESSES = [0x11, 0x12, 0x13]

# Bus number (usually 1 on Pi)
bus = smbus2.SMBus(1)

def read_distance(address):
    try:
        # Read 2 bytes from the sensor
        data = bus.read_i2c_block_data(address, 0, 2)
        # Combine high and low bytes into distance in cm
        distance = data[0] + (data[1] << 8)
        return distance
    except Exception as e:
        print(f"Error reading from 0x{address:02X}: {e}")
        return None

while True:
    for i, addr in enumerate(SENSOR_ADDRESSES):
        dist = read_distance(addr)
        if dist is not None:
            print(f"Sensor {i+1} (0x{addr:02X}): {dist} cm")
        else:
            print(f"Sensor {i+1} (0x{addr:02X}): Read error")
    time.sleep(0.5)
