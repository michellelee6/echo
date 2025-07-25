from picamera2 import Picamera2
from picamera2.previews.qt import QGlPicamera2
from picamera2.outputs import FfmpegOutput
from picamera2.encoders import H264Encoder
from picamera2.encoders import Quality
from picamera2.devices.imx500 import IMX500
import numpy as np
import time

# Initialize Picamera2 and IMX500
picam2 = Picamera2()
imx500 = IMX500()

# Configure the camera for still capture with AI processing
picam2.configure(picam2.create_still_configuration())

picam2.start()
time.sleep(2)

threshold = 0.5  # confidence threshold

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
