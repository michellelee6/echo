import time
from smbus2 import SMBus

I2C_ADDR = 0x10  # Or 0x11 depending on your sensor

def read_distance():
    with SMBus(1) as bus:
        try:
            # Request 9 bytes from the TF-Luna
            data = bus.read_i2c_block_data(I2C_ADDR, 0x00, 9)

            if data[0] == 0x59 and data[1] == 0x59:
                distance = data[2] + (data[3] << 8)  # in cm
                strength = data[4] + (data[5] << 8)
                return distance, strength
            else:
                return None, None
        except Exception as e:
            print("Read failed:", e)
            return None, None

while True:
    dist, strength = read_distance()
    if dist is not None:
        print(f"Distance: {dist} cm | Strength: {strength}")
    else:
        print("Invalid data")
    time.sleep(0.1)
