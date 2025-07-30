import smbus2
import time
import RPi.GPIO as GPIO

# Setup
bus = smbus2.SMBus(1)
MULTIPLEXER_ADDR = 0x70
SENSOR_ADDR = 0x10
SENSOR_CHANNELS = [0, 1, 2, 3, 4]

SENSOR_GPIO = {
    0: 4,
    1: 17,
    2: 27,
    3: 22,
    4: 5
}

THRESHOLDS = {
    "priority": (0, 15),
    "mid": (16, 50),
    "low": (51, 100)
}

GPIO.setmode(GPIO.BCM)
for pin in SENSOR_GPIO.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

def select_mux_channel(channel):
    if 0 <= channel <= 7:
        bus.write_byte(MULTIPLEXER_ADDR, 1 << channel)
    else:
        raise ValueError("Invalid channel")

def read_distance(channel):
    try:
        select_mux_channel(channel)
        time.sleep(0.001)
        data = bus.read_i2c_block_data(SENSOR_ADDR, 0, 9)
        distance = data[0] + (data[1] << 8)
        print(f"Sensor {channel}: Distance = {distance}")  # <-- DEBUG PRINT
        return distance
    except Exception as e:
        print(f"Error reading sensor {channel}: {e}")
        return None

def sensor_control_loop():
    while True:
        results = []

        for ch in SENSOR_CHANNELS:
            dist = read_distance(ch)
            if dist is not None:
                results.append((ch, dist))

        priority = []
        mid = []
        low = []

        for ch, dist in results:
            if THRESHOLDS["priority"][0] <= dist <= THRESHOLDS["priority"][1]:
                priority.append((ch, dist))
            elif THRESHOLDS["mid"][0] <= dist <= THRESHOLDS["mid"][1]:
                mid.append((ch, dist))
            elif THRESHOLDS["low"][0] <= dist <= THRESHOLDS["low"][1]:
                low.append((ch, dist))

        for pin in SENSOR_GPIO.values():
            GPIO.output(pin, GPIO.LOW)

        if priority:
            for ch, _ in priority:
                GPIO.output(SENSOR_GPIO[ch], GPIO.HIGH)
            time.sleep(0.1)
            continue
        elif mid:
            ch, _ = min(mid, key=lambda x: x[1])
            GPIO.output(SENSOR_GPIO[ch], GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(SENSOR_GPIO[ch], GPIO.LOW)
            time.sleep(0.5)
        elif low:
            ch, _ = min(low, key=lambda x: x[1])
            GPIO.output(SENSOR_GPIO[ch], GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(SENSOR_GPIO[ch], GPIO.LOW)
            time.sleep(1.0)
        else:
            time.sleep(0.1)

try:
    sensor_control_loop()
except KeyboardInterrupt:
    print("Stopped by user.")
finally:
    GPIO.cleanup()
