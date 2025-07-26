import smbus2
import time

bus = smbus2.SMBus(1)

SENSOR_ADDRESSES = [0x11, 0x12, 0x13]
FORWARD_SENSOR = 0x12
CALIBRATION_SAMPLES = 20
THRESHOLD_CM = 15  # Trigger box detection if value drops below (baseline - threshold)

def read_distance(address):
    try:
        data = bus.read_i2c_block_data(address, 0, 2)
        return data[0] + (data[1] << 8)
    except Exception as e:
        print(f"Error reading from 0x{address:02X}: {e}")
        return None

# Calibrate the forward sensor
print("Calibrating forward sensor (0x12)...")
calibration_values = []
for _ in range(CALIBRATION_SAMPLES):
    dist = read_distance(FORWARD_SENSOR)
    if dist:
        calibration_values.append(dist)
    time.sleep(0.05)

if calibration_values:
    baseline = sum(calibration_values) / len(calibration_values)
    print(f"Calibration complete. Baseline = {baseline:.1f} cm")
else:
    print("Calibration failed. No valid readings.")
    baseline = None

# Main loop
while True:
    for addr in SENSOR_ADDRESSES:
        dist = read_distance(addr)
        if dist is not None:
            print(f"Sensor 0x{addr:02X}: {dist} cm", end='')

            if addr == FORWARD_SENSOR and baseline is not None:
                if dist < baseline - THRESHOLD_CM:
                    print("  --> Box detected in front!")
                else:
                    print()
            else:
                print()
        else:
            print(f"Sensor 0x{addr:02X}: Read error")
    time.sleep(0.5)
