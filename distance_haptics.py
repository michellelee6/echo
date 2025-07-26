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
    obstacle_detected = False
    min_dist = None

    for i, addr in enumerate(SENSOR_ADDRESSES):
        dist = read_distance(addr)
        if dist is not None:
            if dist < 100:
                print(f"Obstacle detected at sensor 0x{addr:02X}: {dist} cm away")
                obstacle_detected = True
                if min_dist is None or dist < min_dist:
                    min_dist = dist
            else:
                print(f"Sensor {i+1} (0x{addr:02X}): {dist} cm")
        else:
            print(f"Sensor {i+1} (0x{addr:02X}): Read error")

    if obstacle_detected and min_dist is not None:
        blink_delay = ((min_dist ** 2) * 0.1) + 0.05
        GPIO.output(PIN, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(PIN, GPIO.LOW)
        time.sleep(blink_delay)
    else:
        time.sleep(0.1)  # short idle pause to avoid maxing CPU
