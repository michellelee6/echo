import smbus2

# Sensor I2C addresses
SENSOR_ADDRESSES = [0x12, 0x13, 0x14]

# Setup I2C
bus = smbus2.SMBus(1)

def read_distance(address):
    try:
        data = bus.read_i2c_block_data(address, 0, 6)
        return data[2] + (data[3] << 8)
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
