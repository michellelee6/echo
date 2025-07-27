import RPi.GPIO as GPIO
import time

# Define pins to test
test_pins = [4, 14, 15]

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup all pins as output
for pin in test_pins:
    GPIO.setup(pin, GPIO.OUT)

try:
    while True:
        for pin in test_pins:
            print(f"Testing GPIO {pin} - ON")
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(1)
            print(f"Testing GPIO {pin} - OFF")
            GPIO.output(pin, GPIO.LOW)
            time.sleep(1)
except KeyboardInterrupt:
    print("Test stopped by user.")
finally:
    GPIO.cleanup()