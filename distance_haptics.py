import smbus2
import time
import RPi.GPIO as GPIO

# TF-Luna I2C addresses and corresponding GPIO pins
SENSORS = {
    0x11: 17,  # GPIO17 for sensor at 0x11
    0x12: 27,  # GPIO27 for sensor at 0x12
    0x13: 4   # GPIO22 for sensor at 0x13
}

# Set up I2C
bus = smbus2.SMBus(1)

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for pin in SENSORS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

def read_distance(address):
    try:
        data = bus.read_i2c_block_data(address, 0, 2)
        return data[0] + (data[1] << 8)
    except Exception as e:
        print(f"Error reading from 0x{address:02X}: {e}")
        return None

while True:
    for addr, pin in SENSORS.items():
        dist = read_distance(addr)
        if dist is not None:
            if dist < 100:
                print(f"Obstacle detected at sensor 0x{addr:02X}: {dist} cm")
                blink_delay = (dist * 0.1) + 0.05
                GPIO.output(pin, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(pin, GPIO.LOW)
                time.sleep(blink_delay)
            else:
                print(f"Sensor 0x{addr:02X}: {dist} cm - No obstacle")
        else:
            print(f"Sensor 0x{addr:02X}: Read error")
