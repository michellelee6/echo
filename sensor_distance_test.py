import smbus2
import time

bus = smbus2.SMBus(1)

SENSOR_ADDRESSES = {
    'left': 0x11,
    'middle': 0x12,
    'right': 0x13
}

CALIBRATION_SAMPLES = 20
THRESHOLD_CM = 15  # Distance drop needed to consider an object detected

def read_distance(address):
    try:
        data = bus.read_i2c_block_data(address, 0, 2)
        return data[0] + (data[1] << 8)
    except Exception as e:
        print(f"Error reading from 0x{address:02X}: {e}")
        return None

# Step 1: Calibrate all sensors
print("Calibrating sensors...")
baselines = {}
for name, addr in SENSOR_ADDRESSES.items():
    readings = []
    for _ in range(CALIBRATION_SAMPLES):
        dist = read_distance(addr)
        if dist:
            readings.append(dist)
        time.sleep(0.05)
    if readings:
        baselines[name] = sum(readings) / len(readings)
        print(f"  {name} baseline: {baselines[name]:.1f} cm")
    else:
        print(f"  Failed to calibrate {name}")
        baselines[name] = None

print("\nStarting detection...\n")

# Step 2: Live detection loop
while True:
    detections = {}
    for name, addr in SENSOR_ADDRESSES.items():
        dist = read_distance(addr)
        if dist is not None and baselines[name] is not None:
            change = baselines[name] - dist
            print(f"{name.capitalize()} (0x{addr:02X}): {dist} cm", end='')

            if change > THRESHOLD_CM:
                detections[name] = True
                print("  --> Closer")
            else:
                detections[name] = False
                print()
        else:
            print(f"{name.capitalize()} (0x{addr:02X}): Read error")
            detections[name] = None

    # Step 3: Classify object based on detection pattern
    l, m, r = detections.get('left'), detections.get('middle'), detections.get('right')

    if m and not l and not r:
        print(">> Box detected in front!\n")
    elif m and r and not l:
        print(">> Trash detected below!\n")
    elif r and not l and not m:
        print(">> Chair detected on right!\n")
    elif l and m and r:
        print(">> Person detected across all sensors!\n")

    time.sleep(0.5)
