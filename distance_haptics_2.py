import smbus2
import time
import RPi.GPIO as GPIO

# TF-Luna I2C addresses
SENSOR_ADDRESSES = [0x11, 0x12, 0x13]

# Set up I2C
bus = smbus2.SMBus(1)

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
PIN = 4
GPIO.setup(PIN, GPIO.OUT)

def read_distance(address):
    try:
        data = bus.read_i2c_block_data(address, 0, 2)
        return data[0] + (data[1] << 8)
    except Exception as e:
        print(f"Error reading from 0x{address:02X}: {e}")
        return None

while True:
    closest_dist = None

    for i, addr in enumerate(SENSOR_ADDRESSES):
        dist = read_distance(addr)
        if dist is not None:
            print(f"Sensor {i+1} (0x{addr:02X}): {dist} cm")
            if dist < 100:
                # Keep track of the closest obstacle
                if closest_dist is None or dist < closest_dist:
                    closest_dist = dist
        else:
            print(f"Sensor {i+1} (0x{addr:02X}): Read error")

    if closest_dist is not None:
        # Calculate vibration delay: closer = shorter delay
        # Map distance from 0-100 cm to delay between 0.05s (close) and 0.5s (far)
        min_delay = 0.05
        max_delay = 0.5
        # Clamp distance in case it's out of range
        dist_clamped = max(0, min(closest_dist, 100))
        # Invert mapping: closer distance => shorter delay
        delay = min_delay + (max_delay - min_delay) * (dist_clamped / 100)

        # Vibrate motor once
        GPIO.output(PIN, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(PIN, GPIO.LOW)
        time.sleep(delay)
    else:
        # No obstacle detected, keep motor off
        GPIO.output(PIN, GPIO.LOW)
        time.sleep(0.1)