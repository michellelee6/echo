import smbus2
import time
import RPi.GPIO as GPIO

# TF-Luna I2C addresses
SENSOR_ADDRESSES = [0x12, 0x13, 0x14]

# Corresponding GPIO pins for haptic motors
MOTOR_PINS = [4, 14, 15]

# Set up I2C
bus = smbus2.SMBus(1)

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Set up motor pins as output
for pin in MOTOR_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

def read_distance(address):
    try:
        data = bus.read_i2c_block_data(address, 0, 2)
        return data[0] + (data[1] << 8)
    except Exception as e:
        print(f"Error reading from 0x{address:02X}: {e}")
        return None

try:
    while True:
        for i, addr in enumerate(SENSOR_ADDRESSES):
            dist = read_distance(addr)
            if dist is not None:
                if dist < 100:
                    print(f"Obstacle detected at sensor 0x{addr:02X}: {dist} cm away")
                    GPIO.output(MOTOR_PINS[i], GPIO.HIGH)
                else:
                    print(f"Sensor {i+1} (0x{addr:02X}): {dist} cm")
                    GPIO.output(MOTOR_PINS[i], GPIO.LOW)
            else:
                print(f"Sensor {i+1} (0x{addr:02X}): Read error")
                GPIO.output(MOTOR_PINS[i], GPIO.LOW)

        time.sleep(0.05)  # Loop delay

except KeyboardInterrupt:
    print("Stopped by user.")
finally:
    GPIO.cleanup()
