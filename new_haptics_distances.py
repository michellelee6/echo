import smbus2
import time
import threading
import RPi.GPIO as GPIO

# Sensor I2C addresses and corresponding GPIO pins
SENSORS = {
    0x11: 4,
    0x12: 17,
    0x14: 22,
    0x15: 14
}

# Set up I2C
bus = smbus2.SMBus(1)

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for pin in SENSORS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# Store distances and pulse control events
distances = {addr: 999 for addr in SENSORS}
pulse_events = {addr: threading.Event() for addr in SENSORS}

# 2-byte distance reading (your version)
def read_distance(address):
    try:
        data = bus.read_i2c_block_data(address, 0, 2)
        return data[0] + (data[1] << 8)
    except Exception as e:
        print(f"Error reading from 0x{address:02X}: {e}")
        return None

# Pulse function for each sensor, runs continuously in background
def pulse_gpio(addr, pin, event):
    while True:
        event.wait()
        dist = distances[addr]
        on_time = 0.1
        off_time = max(0.01, 0.025 * dist)
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(on_time)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(off_time)

# Start a thread for each sensor’s pulsing
for addr, pin in SENSORS.items():
    t = threading.Thread(target=pulse_gpio, args=(addr, pin, pulse_events[addr]), daemon=True)
    t.start()

# Main loop: sensor logic and GPIO control
try:
    while True:
        readings = []

        # Step 1: Read distances
        for addr, pin in SENSORS.items():
            dist = read_distance(addr)
            if dist is not None:
                distances[addr] = dist
                readings.append({'addr': addr, 'pin': pin, 'dist': dist})
                print(f"Sensor {hex(addr)}: {dist} cm")

        # Step 2: Apply logic
        priority = [r for r in readings if r['dist'] < 15]
        active_addrs = set()

        if priority:
            # Multiple sensors < 15cm → activate all
            for r in priority:
                active_addrs.add(r['addr'])
        else:
            # No priority, check for closest < 100cm
            near = [r for r in readings if r['dist'] < 100]
            if near:
                closest = min(near, key=lambda r: r['dist'])
                active_addrs.add(closest['addr'])

        # Step 3: Set pulse events
        for addr in SENSORS:
            if addr in active_addrs:
                pulse_events[addr].set()
            else:
                pulse_events[addr].clear()
                GPIO.output(SENSORS[addr], GPIO.LOW)

        time.sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()
