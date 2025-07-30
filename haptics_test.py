import smbus2
import time
import RPi.GPIO as GPIO

# Constants
MUX_ADDRESS = 0x70  # Default I2C address for Adafruit TCA9548A
SENSOR_ADDRESS = 0x10  # TF-Luna I2C address

# Multiplexer channels you want to use (change these if needed)
MUX_CHANNELS = [6, 7, 0, 1, 2]  # Easily changeable: e.g., [2, 4, 5, 6, 7]

# Initialize I2C bus
bus = smbus2.SMBus(1)

def select_mux_channel(channel):
    if 0 <= channel <= 7:
        bus.write_byte(MUX_ADDRESS, 1 << channel)
    else:
        raise ValueError("MUX channel must be between 0 and 7")

def read_distance():
    try:
        data = bus.read_i2c_block_data(SENSOR_ADDRESS, 0x00, 9)
        distance = data[0] + (data[1] << 8)
        return distance
    except Exception as e:
        print(f"I2C read error: {e}")
        return None

def main():
    while True:
        for idx, channel in enumerate(MUX_CHANNELS):
            select_mux_channel(channel)
            time.sleep(0.05)  # Give sensor time to stabilize
            distance = read_distance()
            if distance is not None:
                print(f"Sensor {idx} (MUX channel {channel}): {distance} cm")
                if distance < 50:
                    print(f"Haptic {idx} (MUX channel {channel})")
            else:
                print(f"Sensor {idx} (MUX channel {channel}): Read error")
        time.sleep(0.5)  # Delay between sensor rounds

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Stopping program.")
