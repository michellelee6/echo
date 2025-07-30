import smbus2
import time
import RPi.GPIO as GPIO

# Constants
MUX_ADDRESS = 0x70
SENSOR_ADDRESS = 0x10
MUX_CHANNELS = [0, 1, 2, 6, 7]
GPIO_PINS = [4, 17, 27, 22, 14]  # Must match sensor order
THRESHOLD_CM = 50

# Initialize I2C and GPIO
bus = smbus2.SMBus(1)
GPIO.setmode(GPIO.BCM)
for pin in GPIO_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

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
    except:
        return None

def main():
    last_active_idx = None

    try:
        while True:
            distances = []

            for idx, channel in enumerate(MUX_CHANNELS):
                select_mux_channel(channel)
                time.sleep(0.05)
                dist = read_distance()
                if dist is None:
                    dist = float('inf')
                distances.append((idx, dist))

            close_sensors = [d for d in distances if d[1] <= THRESHOLD_CM]
            if close_sensors:
                closest_idx = min(close_sensors, key=lambda x: x[1])[0]
            else:
                closest_idx = None

            # Set GPIO outputs
            for i, pin in enumerate(GPIO_PINS):
                GPIO.output(pin, GPIO.HIGH if i == closest_idx else GPIO.LOW)

            # Only print when there's a change
            if closest_idx != last_active_idx:
                if closest_idx is not None:
                    print(f"Activating haptic on GPIO {GPIO_PINS[closest_idx]}")
                else:
                    print("No sensors within threshold. All haptics OFF.")
                last_active_idx = closest_idx

            time.sleep(0.3)

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
