import time
import smbus2

bus = smbus2.SMBus(1)
I2C_ADDR = 0x10  # Change this if your address is different

def read_tf_luna_raw(addr):
    try:
        write = smbus2.i2c_msg.write(addr, [0x00])
        read = smbus2.i2c_msg.read(addr, 9)
        bus.i2c_rdwr(write, read)
        data = list(read)
        print("Raw:", data)
        if data[0] == 0x59 and data[1] == 0x59:
            return data[2] + data[3] * 256
    except Exception as e:
        print("Error:", e)
    return None

while True:
    d = read_tf_luna_raw(I2C_ADDR)
    print("Distance:", d, "cm")
    time.sleep(0.2)
