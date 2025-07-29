import smbus2
import time
import RPi.GPIO as GPIO
import threading

# Constants
MUX_ADDRESS = 0x70  # Default I2C address for TCA9548A multiplexer
SENSOR_ADDRESS = 0x10  # All sensors share this address

# Mux channels 0 to 4
SENSOR_CHANNELS = {
    0: {"pin": 4, "priority_thresh": 15, "normal_thresh": 100},
    1: {"pin": 17, "priority_thresh": 20, "normal_thresh": 120},  # Custom thresholds
    2: {"pin": 27, "priority_thresh": 15, "normal_thresh": 100},
    3: {"pin": 22, "priority_thresh": 10, "normal_thresh": 90},   # Custom thresholds
    4: {"pin": 14, "priority_thresh": 15, "normal_thresh": 100}
}

bus = smbus2.SMBus(1)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup pins
for sensor in SENSOR_CHANNELS.values():
    GPIO.setup(sensor["pin"], GPIO.OUT)
    GPIO.output(sensor["pin"], GPIO.LOW)

# Select MUX channel
def select_mux_channel(channel):
    if 0 <= channel <= 7:
        bus.write_byte(MUX_ADDRESS, 1 << channel)
    else:
        raise ValueError("MUX channel must be between 0 and 7")

# Read function
def read_distance():
    try:
        data = bus.read_i2c_block_data(SENSOR_ADDRESS, 0, 2)
        return data[0] + (data[1] << 8)
    except Exception as e:
        print(f"Error reading from 0x{SENSOR_ADDRESS:02X}: {e}")
        return None

# Pulse control
def pulse_motor(pin, distance, stop_event):
    while not stop_event.is_set():
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(max(0, 0.05 * distance))

# Main loop
active_thread = None
active_event = None

try:
    while True:
        distances = {}
        for channel in SENSOR_CHANNELS:
            select_mux_channel(channel)
            time.sleep(0.05)  # Allow sensor to stabilize
            dist = read_distance()
            if dist is not None:
                distances[channel] = dist
            print(f"Sensor on channel {channel}: {dist} cm")

        priority_hits = [ch for ch, dist in distances.items()
                         if dist <= SENSOR_CHANNELS[ch]["priority_thresh"]]

        if priority_hits:
            if active_event:
                active_event.set()
            for ch in priority_hits:
                pin = SENSOR_CHANNELS[ch]["pin"]
                stop_event = threading.Event()
                threading.Thread(target=pulse_motor, args=(pin, distances[ch], stop_event), daemon=True).start()
            active_event = None
            active_thread = None

        else:
            on_hits = [(ch, distances[ch]) for ch in distances
                       if distances[ch] <= SENSOR_CHANNELS[ch]["normal_thresh"]]
            if on_hits:
                closest = min(on_hits, key=lambda x: x[1])
                ch = closest[0]
                pin = SENSOR_CHANNELS[ch]["pin"]
                dist = closest[1]

                if active_event:
                    active_event.set()
                active_event = threading.Event()
                active_thread = threading.Thread(target=pulse_motor, args=(pin, dist, active_event), daemon=True)
                active_thread.start()
            else:
                if active_event:
                    active_event.set()
                    active_event = None
                    active_thread = None

        time.sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()