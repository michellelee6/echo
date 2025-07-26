import smbus2
import time

bus = smbus2.SMBus(1)

SENSORS = {
    'left': 0x11,    # pointing up
    'middle': 0x12,  # pointing down
    'right': 0x13    # angled down
}

CALIBRATION_SAMPLES = 20
THRESHOLD = 15  # cm below average to trigger

def read_distance(address):
    try:
        data = bus.read_i2c_block_data(address, 0, 2)
        return data[0] + (data[1] << 8)
    except:
        return None

# Step 1: Calibrate
print("Calibrating sensors...")
averages = {}
for name, addr in SENSORS.items():
    samples = []
    for _ in range(CALIBRATION_SAMPLES):
        d = read_distance(addr)
        if d:
            samples.append(d)
        time.sleep(0.05)
    if samples:
        avg = sum(samples) / len(samples)
        averages[name] = avg
        print(f"  {name}: {avg:.1f} cm")
    else:
        averages[name] = None
        print(f"  {name}: calibration failed.")

print("\nStarting detection...\n")

# Step 2: Main loop
while True:
    status = {}
    for name, addr in SENSORS.items():
        d = read_distance(addr)
        avg = averages.get(name)
        if d is not None and avg is not None:
            active = d < (avg - THRESHOLD)
            status[name] = active
            print(f"{name.capitalize()} ({addr:#04x}): {d} cm {'[ON]' if active else ''}")
        else:
            status[name] = None
            print(f"{name.capitalize()} ({addr:#04x}): Error")

    l, m, r = status.get('left'), status.get('middle'), status.get('right')

    # Step 3: Check combinations
    if m and not l and not r:
        print(">> Box detected\n")
    elif m and r and not l:
        print(">> Trash detected\n")
    elif r and not m and not l:
        print(">> Chair detected\n")
    elif l and m and r:
        print(">> Person detected\n")

    time.sleep(0.5)
