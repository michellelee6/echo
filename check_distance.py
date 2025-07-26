from smbus2 import SMBus
import time

ADDR = 0x10  # change this if you've already updated it

def read_distance(addr):
    with SMBus(1) as bus:
        try:
            # Read 2 bytes starting from register 0x00
            # TF-Luna I2C returns: [low_byte, high_byte]
            data = bus.read_i2c_block_data(addr, 0x00, 2)
            distance = data[0] + (data[1] << 8)  # little-endian
            return distance
        except Exception as e:
            print("Read failed:", e)
            return None

while True:
    dist = read_distance(ADDR)
    if dist is not None:
        print(f"Distance: {dist} cm")
    else:
        print("No reading.")
    time.sleep(0.5)