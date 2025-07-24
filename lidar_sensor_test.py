import time
import smbus2
import math

# Tell case and distances for cases using airpods (AI if neccasary)

# Sensor I2C addresses
I2C_ADDRESSES = {
    "left": 0x11,
    "middle_left": 0x12,    # up
    "middle": 0x13,
    "middle_right": 0x14,   # down
    "right": 0x15
}

# Motor GPIOs
MOTOR_PINS = {
    "left": 17,
    "middle_left": 27,
    "middle": 22,
    "middle_right": 5,
    "right": 6
}

# GPIO setup (commented out for now)
# import RPi.GPIO as GPIO
# GPIO.setmode(GPIO.BCM)
# for pin in MOTOR_PINS.values():
#     GPIO.setup(pin, GPIO.OUT)
#     GPIO.output(pin, GPIO.LOW)

bus = smbus2.SMBus(1)

# Parameters
straight_threshold = 100  # cm
curb_threshold_buffer = 30  # cm
curb_samples = []

# Track current state to avoid repeating same pattern
current_active_state = {}

def read_tf_luna(i2c_addr):
    try:
        write = smbus2.i2c_msg.write(i2c_addr, [0x00])
        read = smbus2.i2c_msg.read(i2c_addr, 9)
        bus.i2c_rdwr(write, read)
        data = list(read)
        if len(data) == 9 and data[0] == 0x59 and data[1] == 0x59:
            distance = data[2] + data[3] * 256
            return distance
    except Exception as e:
        print(f"Error reading from {hex(i2c_addr)}: {e}")
    return None

def buzz_pattern(motor_list, pattern, delay=0.1):
    for duration in pattern:
        # for motor in motor_list:
        #     GPIO.output(MOTOR_PINS[motor], GPIO.HIGH)
        time.sleep(duration)
        # for motor in motor_list:
        #     GPIO.output(MOTOR_PINS[motor], GPIO.LOW)
        time.sleep(delay)

def set_motor_state(motor_list, on):
    # for motor in motor_list:
    #     GPIO.output(MOTOR_PINS[motor], GPIO.HIGH if on else GPIO.LOW)
    pass

def update_motor_feedback(motor_list, description):
    key = tuple(sorted(motor_list))
    if current_active_state.get(key) != description:
        print(f"Buzzing motors: {motor_list} --> {description}")
        # Choose pattern
        if "obstacle close" in description:
            buzz_pattern(motor_list, [0.3])
        elif "Curb detected" in description:
            buzz_pattern(motor_list, [0.2, 0.2])
        elif "Drop detected" in description:
            buzz_pattern(motor_list, [0.6])
        elif "Wall" in description:
            buzz_pattern(motor_list, [0.2, 0.2, 0.2], delay=0.1)
        current_active_state[key] = description

    set_motor_state(motor_list, True)

def clear_motor_feedback():
    keys_to_remove = []
    for key in current_active_state:
        keys_to_remove.append(key)
        set_motor_state(list(key), False)
    for key in keys_to_remove:
        del current_active_state[key]

def wall_detect(straight_cm, down_cm, tolerance=15):
    if straight_cm is None or down_cm is None:
        return False
    expected_hyp = math.hypot(straight_cm, down_cm)
    return abs(expected_hyp - straight_cm) < tolerance

print("Starting sensor loop (distances in cm)...")
try:
    while True:
        distances = {name: read_tf_luna(addr) for name, addr in I2C_ADDRESSES.items()}
        print("Distances (cm):", distances)

        event_triggered = False

        # Maintain running average for middle-right (down)
        if distances["middle_right"]:
            curb_samples.append(distances["middle_right"])
            if len(curb_samples) > 30:
                curb_samples.pop(0)

        # Front obstacle detection
        for name in ["left", "middle", "right"]:
            if distances[name] and distances[name] < straight_threshold:
                update_motor_feedback([name], f"{name} obstacle close")
                event_triggered = True

        # Curb/drop detection
        if len(curb_samples) == 30 and distances["middle_right"] is not None:
            avg_down = sum(curb_samples) / len(curb_samples)
            current_down = distances["middle_right"]
            delta = avg_down - current_down
            if delta > curb_threshold_buffer:
                update_motor_feedback(list(MOTOR_PINS), "Curb detected (rise)")
                event_triggered = True
            elif delta < -curb_threshold_buffer:
                update_motor_feedback(list(MOTOR_PINS), "Drop detected")
                event_triggered = True

        # Wall detection
        if wall_detect(distances["right"], distances["middle_right"]):
            update_motor_feedback(["middle_right", "right"], "Wall on right")
            event_triggered = True
        if wall_detect(distances["left"], distances["middle_right"]):
            update_motor_feedback(["middle_right", "left"], "Wall on left")
            event_triggered = True
        if wall_detect(distances["middle"], distances["middle_left"]):
            update_motor_feedback(["left", "middle", "right"], "Wall ahead")
            event_triggered = True

        if not event_triggered:
            clear_motor_feedback()

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting...")
# finally:
#     GPIO.cleanup()