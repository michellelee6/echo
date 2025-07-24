import smbus2
import time

TF_LUNA_ADDR = 0x10
REGISTER = 0x00
bus = smbus2.SMBus(1)

def read_distance():
    try:
        data = bus.read_i2c_block_data(TF_LUNA_ADDR, REGISTER, 9)
        print("Raw I2C data:", data)

        # Try interpreting bytes 2 and 3 as distance (like UART)
        distance = data[2] + (data[3] << 8)
        print(f"Guessed Distance: {distance} cm")

    except Exception as e:
        print("Error:", e)

while True:
    read_distance()
    time.sleep(0.2)
