import smbus2
import time
import RPi.GPIO as GPIO

MUX_ADDR = 0x70
TF_LUNA_ADDR = 0x10
bus = smbus2.SMBus(1)

SENSORS = [
    {"mux": 0, "gpio": 4},
    {"mux": 1, "gpio": 17},
    {"mux": 2, "gpio": 27},
    {"mux": 3, "gpio": 22},
    {"mux": 4, "gpio": 14},
]

THRESHOLDS = {
    "priority": (0, 15),
    "tier2": (16, 50),
    "tier3": (51, 100),
}

GPIO.setmode(GPIO.BCM)
for s in SENSORS:
    GPIO.setup(s["gpio"], GPIO.OUT)
    GPIO.output(s["gpio"], GPIO.LOW)

def mux_select(channel):
    bus.write_byte(MUX_ADDR, 1 << channel)

def read_distance():
    try:
        d = bus.read_i2c_block_data(TF_LUNA_ADDR, 0x00, 9)
        return d[2] + d[3]*256
    except:
        return None

def get_status(d):
    if d is None:
        return None
    if THRESHOLDS["priority"][0] <= d <= THRESHOLDS["priority"][1]:
        return "priority"
    if THRESHOLDS["tier2"][0] <= d <= THRESHOLDS["tier2"][1]:
        return "tier2"
    if THRESHOLDS["tier3"][0] <= d <= THRESHOLDS["tier3"][1]:
        return "tier3"
    return None

while True:
    data = []
    for s in SENSORS:
        mux_select(s["mux"])
        time.sleep(0.01)
        d = read_distance()
        status = get_status(d)
        data.append({"gpio": s["gpio"], "status": status, "dist": d})

    p = [x for x in data if x["status"] == "priority"]
    if p:
        for x in data:
            GPIO.output(x["gpio"], GPIO.HIGH if x in p else GPIO.LOW)
        continue

    t2 = [x for x in data if x["status"] == "tier2"]
    t3 = [x for x in data if x["status"] == "tier3"]

    active = None
    if t2:
        active = min(t2, key=lambda x: x["dist"])
        GPIO.output(active["gpio"], GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(active["gpio"], GPIO.LOW)
        time.sleep(0.5)
    elif t3:
        active = min(t3, key=lambda x: x["dist"])
        GPIO.output(active["gpio"], GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(active["gpio"], GPIO.LOW)
        time.sleep(1)
    else:
        for x in data:
            GPIO.output(x["gpio"], GPIO.LOW)
