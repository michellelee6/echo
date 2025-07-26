import smbus2
import RPi.GPIO as GPIO

# Sensor I2C addresses and corresponding GPIO pins
SENSOR_ADDRESSES = [0x12, 0x13, 0x14]
GPIO_PINS = [4, 14, 15]

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for pin in GPIO_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# Setup I2C
bus = smbus2.SMBus(1)

def read_distance(address):
    try:
        data = bus.read_i2c_block_data(address, 0, 6)
        return data[2] + (data[3] << 8)
    except:
        return None

while True:
    for i in range(3):
        dist = read_distance(SENSOR_ADDRESSES[i])
        if dist is not None and dist < 100:
            print(f"Obstacle detected {dist} cm away")
            GPIO.output(GPIO_PINS[i], GPIO.HIGH)
        else:
            GPIO.output(GPIO_PINS[i], GPIO.LOW)
