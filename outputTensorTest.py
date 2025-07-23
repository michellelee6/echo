from picamera2 import Picamera2
from imx500 import IMX500

picam2 = Picamera2()
picam2.start()

# Give the camera a second to warm up
import time
time.sleep(1)

# Capture metadata (frame isn't needed unless you want to display/save it)
metadata = picam2.capture_metadata()

# Get AI detection outputs
outputs = IMX500.get_outputs(metadata)

# Optional: label map for readability
labels = {
    0: "background",
    1: "person",
    2: "bicycle",
    3: "car",
    # Add more if needed...
}

for o in outputs:
    label_id = o["label"]
    label = labels.get(label_id, f"unknown ({label_id})")
    conf = o["confidence"]
    bbox = o["bbox"]
    print(f"Detected {label} with confidence {conf:.2f}, bbox={bbox}")
