from picamera2 import Picamera2
from picamera2.devices.imx500 import IMX500
import time

# Initialize Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())

# Correct: pass both the picamera object and the post-process file
imx500 = IMX500(picam2, "/usr/share/rpi-camera-assets/imx500_mobilenet_ssd.json")

picam2.start()
time.sleep(2)

while True:
    metadata = picam2.capture_metadata()
    outputs = imx500.get_outputs(metadata, add_batch=True)

    if outputs is None or len(outputs) != 4:
        continue

    boxes, classes, scores, num_detections = outputs

    print("\n--- New Frame ---")
    print("Num detections:", num_detections)
    print("Classes:", classes)
    print("Scores:", scores)
    print("Boxes:", boxes)

    time.sleep(1)
