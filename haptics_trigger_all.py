import smbus2
import time
import RPi.GPIO as GPIO

# Constants
MUX_ADDRESS = 0x70
SENSOR_ADDRESS = 0x10
MUX_CHANNELS = [6, 7, 0, 1, 2]  # Sensors 0–4

# New GPIO pin configuration for haptics
# Left side: GPIO 5, GPIO 6
# Right side: GPIO 27, GPIO 22
HAPTIC_PINS = [5, 6, 27, 22]

THRESHOLD_CM = 65

# Init I2C and GPIO
bus = smbus2.SMBus(1)
GPIO.setmode(GPIO.BCM)
for pin in HAPTIC_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

def select_mux_channel(channel):
    if 0 <= channel <= 7:
        bus.write_byte(MUX_ADDRESS, 1 << channel)
    else:
        raise ValueError("MUX channel must be 0–7")

def read_distance():
    try:
        data = bus.read_i2c_block_data(SENSOR_ADDRESS, 0x00, 9)
        return data[0] + (data[1] << 8)
    except Exception as e:
        print(f"I2C read error: {e}")
        return None

def main():
    try:
        while True:
            distances = []
            haptics = []

            for idx, channel in enumerate(MUX_CHANNELS):
                select_mux_channel(channel)
                time.sleep(0.05)
                distance = read_distance()
                distances.append((idx, channel, distance))

                if distance is not None:
                    print(f"Sensor {idx} (MUX {channel}): {distance} cm")
                    if distance < THRESHOLD_CM:
                        haptics.append((idx, channel, distance))
                else:
                    print(f"Sensor {idx} (MUX {channel}): Read error")

            print("---")

            # Determine and activate the closest haptic
            if haptics:
                closest = min(haptics, key=lambda x: x[2])
                closest_idx = closest[0]

                # Map sensor index to haptic motor:
                # Sensor 0, 1 → Left (GPIO 5, 6)
                # Sensor 2, 3 → Right (GPIO 27, 22)
                # Sensor 4 (middle) → trigger both left and right

                for pin in HAPTIC_PINS:
                    GPIO.output(pin, GPIO.LOW)  # Turn all off initially

                if closest_idx == 0:
                    GPIO.output(5, GPIO.HIGH)
                elif closest_idx == 1:
                    GPIO.output(6, GPIO.HIGH)
                elif closest_idx == 2:
                    GPIO.output(27, GPIO.HIGH)
                elif closest_idx == 3:
                    GPIO.output(22, GPIO.HIGH)
                elif closest_idx == 4:
                    # Middle sensor → activate all
                    for pin in HAPTIC_PINS:
                        GPIO.output(pin, GPIO.HIGH)

                print(f">>> Haptic triggered by Sensor {closest_idx} at {closest[2]} cm")

            else:
                # No haptics triggered
                for pin in HAPTIC_PINS:
                    GPIO.output(pin, GPIO.LOW)

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
