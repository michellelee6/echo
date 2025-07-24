import smbus2
import time

# I2C address of the TF-Luna (default is 0x10)
I2C_ADDR = 0x10
bus = smbus2.SMBus(1)  # Use I2C bus 1 on Raspberry Pi

def read_distance():
    try:
        while True:
            # Request 9 bytes from the sensor
            data = bus.read_i2c_block_data(I2C_ADDR, 0, 9)

            # Check frame header
            if data[0] == 0x59 and data[1] == 0x59:
                distance = data[2] + (data[3] << 8)      # in cm
                strength = data[4] + (data[5] << 8)
                temperature = (data[6] + (data[7] << 8)) / 8.0 - 256

                print(f"Distance: {distance} cm | Strength: {strength} | Temp: {temperature:.1f}°C")
            else:
                print("Invalid data received")
            
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Stopped by user")

if __name__ == "__main__":
    read_distance()
