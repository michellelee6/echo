import smbus2
import time
import RPi.GPIO as GPIO

# TF-Luna I2C addresses
SENSOR_ADDRESSES = [0x12, 0x13, 0x14]
GPIO_PINS = [4, 15, 14]  # Mapped to sensors in order

# Setup I2C
bus = smbus2.SMBus(1)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for pin in GPIO_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

def read_distance(address):
    try:
        # Read 2 bytes from the sensor (High byte first)
        data = bus.read_i2c_block_data(address, 0, 2)
        distance = (data[0] << 8) + data[1]
        return distance
    except Exception as e:
        print(f"Error reading from 0x{address:02X}: {e}")
        return None

while True:
    for i, addr in enumerate(SENSOR_ADDRESSES):
        dist = read_distance(addr)
        if dist is not None:
            print(f"Sensor {i+1} (0x{addr:02X}): {dist} cm")
            if dist < 100:
                GPIO.output(GPIO_PINS[i], GPIO.HIGH)
            else:
                GPIO.output(GPIO_PINS[i], GPIO.LOW)
        else:
            print(f"Sensor {i+1} (0x{addr:02X}): Read error")
    time.sleep(0.5)
