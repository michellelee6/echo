import smbus2
import time
import RPi.GPIO as GPIO

# Constants
MUX_ADDRESS = 0x70
SENSOR_ADDRESS = 0x10
MUX_CHANNELS = [6, 7, 0, 1, 2]
GPIO_PINS = [4, 17, 27, 22, 5]  # GPIO pins for sensors 0–4
THRESHOLD_CM = 50

# Init I2C and GPIO
bus = smbus2.SMBus(1)
GPIO.setmode(GPIO.BCM)
for pin in GPIO_PINS:
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

            # Determine and activate closest haptic
            if haptics:
                closest = min(haptics, key=lambda x: x[2])  # Smallest distance
                closest_idx = closest[0]

                # Activate only closest haptic
                for i, pin in enumerate(GPIO_PINS):
                    GPIO.output(pin, GPIO.HIGH if i == closest_idx else GPIO.LOW)

                print(f">>> Haptic triggered: Sensor {closest_idx} at {closest[2]} cm")
            else:
                # No valid haptic, turn all off
                for pin in GPIO_PINS:
                    GPIO.output(pin, GPIO.LOW)

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
