import time
import math
import smbus2

# --- Sensor angles & trig precompute ---
alpha1 = math.radians(70)
alpha2 = math.radians(55)
alpha3 = math.radians(45)
sin1, cos1 = math.sin(alpha1), math.cos(alpha1)
sin2, cos2 = math.sin(alpha2), math.cos(alpha2)
sin3, cos3 = math.sin(alpha3), math.cos(alpha3)

# --- Real-world height constants (cm) ---
SEAT_HEIGHT = 45
BACK_HEIGHT = 80
PERSON_MIN  = 150
PERSON_MAX  = 180

# --- Tunable thresholds (cm) ---
WALK_THRESH      =  100   # noise band
SAME_OBJ_THRESH  = 100   # horizontal grouping
DROP_THRESH     = -100   # cm avg below floor → drop
CURB_MIN, CURB_MAX = 100, 300
BOX_THRESH       = 300

# --- I2C setup ---
bus = smbus2.SMBus(1)
addrs = {'S1':0x11, 'S2':0x12, 'S3':0x13}

def read_dist(addr):
    """Read distance (cm) from TF-Luna at I2C addr"""
    bus.write_i2c_block_data(addr, 0x03, [])
    time.sleep(0.01)
    d = bus.read_i2c_block_data(addr, 0x00, 9)
    return d[1] | (d[2] << 8)


def read_all():
    return {k: read_dist(v) for k,v in addrs.items()}


def calibrate(samples=50):
    print("Calibrating... keep sensors clear")
    s1_vals, s2_vals = [], []
    for _ in range(samples):
        d = read_all()
        s1_vals.append(d['S1'])
        s2_vals.append(d['S2'])
        time.sleep(0.05)
    S1_0 = sum(s1_vals)/samples
    S2_0 = sum(s2_vals)/samples
    H = (S1_0*sin1 + S2_0*sin2) / 2
    print(f"Calibration complete: belt height H = {H:.1f} cm")
    return S1_0, S2_0, H


def classify(S1, S2, S3, S1_0, S2_0, H):
    # Compute horizontal distances
    r1 = S1 * cos1
    r2 = S2 * cos2
    r3 = S3 * cos3

    # Compute vertical offsets from floor
    y1 = H - S1 * sin1
    y2 = H - S2 * sin2
    y3 = H + S3 * sin3
    
    delta_y = (y1 + y2) / 2

    # 1. Drop
    if delta_y < DROP_THRESH:
        return f"Drop ({abs(delta_y):.1f} cm)"
    # 2. Curb
    if CURB_MIN <= delta_y <= CURB_MAX:
        return f"Curb ({delta_y:.1f} cm)"
    # 3. Box
    if delta_y > BOX_THRESH:
        return f"Box ({delta_y:.1f} cm)"
    # 4. Chair seat
    if (SEAT_HEIGHT - WALK_THRESH) <= y2 <= (SEAT_HEIGHT + WALK_THRESH) and abs(delta_y) <= WALK_THRESH:
        return "Chair seat"
    # 5. Chair back
    if (BACK_HEIGHT - WALK_THRESH) <= y3 <= (BACK_HEIGHT + WALK_THRESH) and abs(delta_y) <= WALK_THRESH:
        return "Chair back"
    # 6. Person
    if abs(y1) <= WALK_THRESH and abs(y2) <= WALK_THRESH and PERSON_MIN <= y3 <= PERSON_MAX:
        return "Person"

# --- Main loop ---
S1_0, S2_0, H = calibrate()
while True:
    d = read_all()
    result = classify(d['S1'], d['S2'], d['S3'], S1_0, S2_0, H)
    print(f"S1={d['S1']:4d}, S2={d['S2']:4d}, S3={d['S3']:4d} -> {result}")
    time.sleep(0.1)
