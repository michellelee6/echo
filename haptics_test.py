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
    except Exception as e:
        print(f"I2C read error: {e}")
        return None

def main():
    try:
        while True:
            distances = []

            print("\n--- Scanning Sensors ---")
            for idx, channel in enumerate(MUX_CHANNELS):
                select_mux_channel(channel)
                time.sleep(0.05)
                dist = read_distance()
                if dist is not None:
                    print(f"Sensor {idx} (MUX Ch {channel}) → Distance: {dist} cm")
                else:
                    print(f"Sensor {idx} (MUX Ch {channel}) → Read Error")
                    dist = float('inf')
                distances.append((idx, dist))

            close_sensors = [d for d in distances if d[1] <= THRESHOLD_CM]
            if close_sensors:
                closest_idx = min(close_sensors, key=lambda x: x[1])[0]
                print(f">>> Activating haptic for Sensor {closest_idx} (GPIO {GPIO_PINS[closest_idx]}) <<<")
            else:
                closest_idx = None
                print(">>> No sensors within threshold. All haptics OFF.")

            # Set GPIO outputs
            for i, pin in enumerate(GPIO_PINS):
                if i == closest_idx:
                    GPIO.output(pin, GPIO.HIGH)
                else:
                    GPIO.output(pin, GPIO.LOW)

            time.sleep(0.3)

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
