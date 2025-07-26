import smbus2

# TF-Luna sensor I2C addresses
SENSOR_ADDRESSES = [0x12, 0x13, 0x14]

# Set up I2C
bus = smbus2.SMBus(1)

def read_distance(address):
    try:
        # Read 2 bytes: High byte first, then low byte
        data = bus.read_i2c_block_data(address, 0, 2)
        distance = (data[0] << 8) + data[1]
        return distance
    except:
        return None

while True:
    for address in SENSOR_ADDRESSES:
        dist = read_distance(address)
        if dist is not None:
            if dist < 100:
                print(f"Sensor 0x{address:02X}: {dist} cm - Obstacle detected")
            else:
                print(f"Sensor 0x{address:02X}: {dist} cm")
