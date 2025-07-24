import smbus2
import time

TF_LUNA_ADDR = 0x10
REGISTER = 0x00
bus = smbus2.SMBus(1)

def read_distance():
    try:
        data = bus.read_i2c_block_data(TF_LUNA_ADDR, REGISTER, 9)
        print("Raw I2C data:", data)

        if data[0] == 0x5A and data[1] == 0x5A:
            distance = data[2] + (data[3] << 8)
            strength = data[4] + (data[5] << 8)
            print(f"Distance: {distance} cm | Strength: {strength}")
        else:
            print("Invalid data header.")
    except Exception as e:
        print("Error:", e)

while True:
    read_distance()
    time.sleep(0.1)
