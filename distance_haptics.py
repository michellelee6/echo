import smbus2
import time
import RPi.GPIO as GPIO

# I2C addresses for the TF-Luna sensors
SENSOR_ADDRESSES = [0x12, 0x13, 0x14]
GPIO_PINS = [4, 14, 15]

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for pin in GPIO_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# Initialize I2C
bus = smbus2.SMBus(1)

def read_distance(address):
    try:
        # TF-Luna sends 6 bytes, distance is bytes 3 and 2 (LSB first)
        data = bus.read_i2c_block_data(address, 0, 6)
        distance = data[2] + (data[3] << 8)
        return distance
    except Exception as e:
        print(f"Error reading from 0x{address:02X}: {e}")
        return None

while True:
    for i, address in enumerate(SENSOR_ADDRESSES):
        distance = read_distance(address)
        if distance is not None:
            if distance < 100:
                print(f"Obstacle detected {distance} cm away at sensor 0x{address:02X}")
                GPIO.output(GPIO_PINS[i], GPIO.HIGH)
            else:
                GPIO.output(GPIO_PINS[i], GPIO.LOW)
    time.sleep(0.1)
