import time
import smbus2

bus = smbus2.SMBus(1)
I2C_ADDR = 0x10

def read_tf_luna(i2c_addr):
    try:
        write = smbus2.i2c_msg.write(i2c_addr, [0x00])
        read = smbus2.i2c_msg.read(i2c_addr, 9)
        bus.i2c_rdwr(write, read)
        data = list(read)
        if len(data) == 9 and data[0] == 0x59 and data[1] == 0x59:
            distance = data[2] + data[3] * 256
            return distance
    except Exception as e:
        print(f"Error reading from {hex(i2c_addr)}: {e}")
    return None

print("Reading from TF-Luna at 0x10...")
try:
    while True:
        distance = read_tf_luna(I2C_ADDR)
        print(f"Distance: {distance} cm")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Stopped.")