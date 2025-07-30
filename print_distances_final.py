import smbus2
import time

# Constants
MUX_ADDR = 0x70  # I2C address of TCA9548A multiplexer
TF_LUNA_ADDR = 0x10  # I2C address of each TF-Luna sensor
MUX_CHANNELS = [0, 1, 2, 3, 4]  # Channels where sensors are connected

# I2C bus
bus = smbus2.SMBus(1)  # Use 1 for Raspberry Pi

def select_mux_channel(channel):
    if 0 <= channel <= 7:
        bus.write_byte(MUX_ADDR, 1 << channel)
    else:
        raise ValueError("Channel must be 0-7")

def read_tf_luna():
    try:
        data = bus.read_i2c_block_data(TF_LUNA_ADDR, 0, 9)
        distance = data[2] + (data[3] << 8)
        return distance
    except Exception as e:
        print(f"Read error: {e}")
        return None

def main():
    while True:
        for channel in MUX_CHANNELS:
            select_mux_channel(channel)
            time.sleep(0.005)  # Short delay for switching
            distance = read_tf_luna()
            if distance is not None:
                print(f"Sensor {channel}: {distance} cm")
            else:
                print(f"Sensor {channel}: Read failed")
        print("-" * 30)
        time.sleep(0.5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Stopped by user")