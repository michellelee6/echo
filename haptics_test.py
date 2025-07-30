import smbus2
import time
import RPi.GPIO as GPIO
import threading

# Constants
MUX_ADDRESS = 0x70
SENSOR_ADDRESS = 0x10
NUM_SENSORS = 5

# Sensor settings per MUX channel
SENSOR_CONFIG = {
    6: {"pin": 4, "priority": 15, "normal": 100},
    7: {"pin": 17, "priority": 15, "normal": 100},
    4: {"pin": 27, "priority": 15, "normal": 100},
    1: {"pin": 22, "priority": 15, "normal": 100},
    2: {"pin": 14, "priority": 15, "normal": 100},
}

bus = smbus2.SMBus(1)
GPIO.setmode(GPIO.BCM)

for config in SENSOR_CONFIG.values():
    GPIO.setup(config["pin"], GPIO.OUT)
    GPIO.output(config["pin"], GPIO.LOW)

buzzing_flags = {ch: False for ch in SENSOR_CONFIG}
buzzing_threads = {}

def select_mux_channel(channel):
    if 0 <= channel <= 7:
        bus.write_byte(MUX_ADDRESS, 1 << channel)
        time.sleep(0.001)

def read_distance(channel):
    try:
        select_mux_channel(channel)
        data = bus.read_i2c_block_data(SENSOR_ADDRESS, 0, 2)
        return data[0] + (data[1] << 8)
    except Exception as e:
        print(f"[CH{channel}] Error: {e}")
        return None

def buzz_pattern(channel, pin, distance, priority, normal):
    while buzzing_flags[channel]:
        if distance <= priority:
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(0.1)
        elif distance <= priority * 1.5:
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(pin, GPIO.LOW)
            time.sleep(0.5)
        elif distance <= normal:
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(pin, GPIO.LOW)
            time.sleep(1.0)
        else:
            GPIO.output(pin, GPIO.LOW)
            time.sleep(0.1)

def sensor_loop():
    while True:
        for ch in range(NUM_SENSORS):
            cfg = SENSOR_CONFIG[ch]
            dist = read_distance(ch)
            if dist is None:
                continue

            pin = cfg["pin"]
            priority = cfg["priority"]
            normal = cfg["normal"]

            if dist <= normal:
                if not buzzing_flags[ch]:
                    buzzing_flags[ch] = True
                    thread = threading.Thread(target=buzz_pattern, args=(ch, pin, dist, priority, normal))
                    thread.start()
                    buzzing_threads[ch] = thread
            else:
                if buzzing_flags[ch]:
                    buzzing_flags[ch] = False
                    GPIO.output(pin, GPIO.LOW)

        time.sleep(0.05)

try:
    sensor_loop()
except KeyboardInterrupt:
    print("Stopping...")
finally:
    for ch in buzzing_flags:
        buzzing_flags[ch] = False
    GPIO.cleanup()
