from picamera2 import Picamera2
from picamera2.devices import IMX500
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput
import numpy as np
import time

picam2 = Picamera2()
imx500 = IMX500(picam2)
picam2.start()

while True:
    metadata = picam2.capture_metadata()
    outputs = imx500.get_outputs(metadata, add_batch=True)

    if outputs is None or len(outputs) != 4:
        continue

    boxes, class_scores, scores, num_detections = outputs

    print("Class scores shape:", np.array(class_scores).shape)
    print("Class scores sample:", class_scores[0])
    print("Boxes:", boxes[0])
    print("Scores:", scores[0])
    print("Num detections:", num_detections)

    time.sleep(1)
