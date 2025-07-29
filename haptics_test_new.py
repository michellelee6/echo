import smbus2
import time
import RPi.GPIO as GPIO
import threading

# Constants
MUX_ADDRESS = 0x70  # Default I2C address for TCA9548A multiplexer
SENSOR_ADDRESS = 0x10  # All sensors share this address

# Sensor channels with thresholds and GPIOs
SENSOR_CHANNELS = {
    0: {"pin": 4, "priority_thresh": 5, "normal_thresh": 100},
    1: {"pin": 17, "priority_thresh": 5, "normal_thresh": 100},  # Custom thresholds
    2: {"pin": 27, "priority_thresh": 5, "normal_thresh": 100},
    3: {"pin": 22, "priority_thresh": 5, "normal_thresh": 100},   # Custom thresholds
    4: {"pin": 14, "priority_thresh": 5, "normal_thresh": 100}
}

# Add control structures to each sensor
for sensor in SENSOR_CHANNELS.values():
    sensor["event"] = threading.Event()
    sensor["thread"] = None
    sensor["active"] = False
    sensor["last_distance"] = None

bus = smbus2.SMBus(1)

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for sensor in SENSOR_CHANNELS.values():
    GPIO.setup(sensor["pin"], GPIO.OUT)
    GPIO.output(sensor["pin"], GPIO.LOW)

# Select MUX channel
def select_mux_channel(channel):
    if 0 <= channel <= 7:
        bus.write_byte(MUX_ADDRESS, 1 << channel)
    else:
        raise ValueError("MUX channel must be between 0 and 7")

# Read distance (2-byte TF-Luna style)
def read_distance():
    try:
        data = bus.read_i2c_block_data(SENSOR_ADDRESS, 0, 2)
        return data[0] + (data[1] << 8)
    except Exception as e:
        print(f"Error reading from sensor: {e}")
        return None

# Start pulsing
def start_pulsing(sensor):
    def pulse():
        while sensor["event"].is_set():
            GPIO.output(sensor["pin"], GPIO.HIGH)
            time.sleep(0.1)
            distance = sensor["last_distance"] or 100
            GPIO.output(sensor["pin"], GPIO.LOW)
            time.sleep(max(0.05 * distance, 0.05))
    if not sensor["thread"] or not sensor["thread"].is_alive():
        sensor["event"].set()
        sensor["thread"] = threading.Thread(target=pulse, daemon=True)
        sensor["thread"].start()
    sensor["active"] = True

# Stop pulsing
def stop_pulsing(sensor):
    if sensor["active"]:
        sensor["event"].clear()
        GPIO.output(sensor["pin"], GPIO.LOW)
        sensor["active"] = False

# Main loop
try:
    while True:
        distances = {}
        for ch, sensor in SENSOR_CHANNELS.items():
            select_mux_channel(ch)
            time.sleep(0.05)
            dist = read_distance()
            if dist is not None:
                distances[ch] = dist
                sensor["last_distance"] = dist
                print(f"Sensor on channel {ch}: {dist} cm")

        # Find priority hits
        priority_hits = [ch for ch, dist in distances.items()
                         if dist <= SENSOR_CHANNELS[ch]["priority_thresh"]]

        active_channels = []

        if priority_hits:
            # Priority case: multiple allowed
            active_channels = priority_hits
        else:
            # Find closest below normal threshold
            on_hits = [(ch, dist) for ch, dist in distances.items()
                       if dist <= SENSOR_CHANNELS[ch]["normal_thresh"]]
            if on_hits:
                closest = min(on_hits, key=lambda x: x[1])
                active_channels = [closest[0]]

        # Update each sensor's state
        for ch, sensor in SENSOR_CHANNELS.items():
            if ch in active_channels:
                start_pulsing(sensor)
            else:
                stop_pulsing(sensor)

        time.sleep(0.1)

except KeyboardInterrupt:
    for sensor in SENSOR_CHANNELS.values():
        stop_pulsing(sensor)
    GPIO.cleanup()