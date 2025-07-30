import smbus2
import time
import RPi.GPIO as GPIO
import threading

# Constants
MUX_ADDRESS = 0x70
SENSOR_ADDRESS = 0x10

# Sensor configuration: MUX channel -> {GPIO pin, priority threshold, normal threshold}
SENSOR_CONFIG = {
    6: {"pin": 4, "priority": 15, "normal": 100},
    7: {"pin": 17, "priority": 15, "normal": 100},
    0: {"pin": 27, "priority": 15, "normal": 100},
    1: {"pin": 22, "priority": 15, "normal": 100},
    2: {"pin": 14, "priority": 15, "normal": 100},
}

bus = smbus2.SMBus(1)
GPIO.setmode(GPIO.BCM)

# Setup GPIO pins
for cfg in SENSOR_CONFIG.values():
    GPIO.setup(cfg["pin"], GPIO.OUT)
    GPIO.output(cfg["pin"], GPIO.LOW)

# Threading and control structures
buzzing_flags = {ch: False for ch in SENSOR_CONFIG}
buzzing_threads = {}
distance_lock = threading.Lock()
latest_distances = {ch: 9999 for ch in SENSOR_CONFIG}

def select_mux_channel(channel):
    if 0 <= channel <= 7:
        bus.write_byte(MUX_ADDRESS, 1 << channel)
        time.sleep(0.01)

def read_distance(channel):
    try:
        select_mux_channel(channel)
        data = bus.read_i2c_block_data(SENSOR_ADDRESS, 0, 2)
        return data[0] + (data[1] << 8)
    except Exception as e:
        print(f"[CH{channel}] Error: {e}")
        return None

def buzz_pattern(channel, pin, priority, normal):
    while buzzing_flags[channel]:
        with distance_lock:
            distance = latest_distances[channel]

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
            time.sleep(0.2)

def sensor_loop():
    while True:
        for ch, cfg in SENSOR_CONFIG.items():
            dist = read_distance(ch)
            if dist is None:
                continue

            # Update latest distance
            with distance_lock:
                latest_distances[ch] = dist

            pin = cfg["pin"]
            priority = cfg["priority"]
            normal = cfg["normal"]

            if dist <= normal:
                if not buzzing_flags[ch]:
                    buzzing_flags[ch] = True
                    thread = threading.Thread(target=buzz_pattern, args=(ch, pin, priority, normal))
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
    time.sleep(1)  # Allow threads to exit
    GPIO.cleanup()
