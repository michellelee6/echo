import time
import smbus2

bus = smbus2.SMBus(1)
I2C_ADDR = 0x10  # Update this if your sensor uses a different address

def read_tf_luna(addr):
    try:
        write = smbus2.i2c_msg.write(addr, [0x00])
        read = smbus2.i2c_msg.read(addr, 9)
        bus.i2c_rdwr(write, read)
        data = list(read)
        if data[0] == 0x59 and data[1] == 0x59:
            return data[2] + (data[3] << 8)
    except:
        pass
    return None

while True:
    distance = read_tf_luna(I2C_ADDR)
    if distance is not None:
        print(distance)
    time.sleep(0.2)
