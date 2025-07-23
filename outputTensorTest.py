import argparse
from picamera2 import Picamera2
from picamera2.devices import IMX500
from picamera2.devices.imx500 import NetworkIntrinsics
import numpy as np

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        type=str,
        default="/usr/share/imx500-models/imx500_network_ssd_mobilenetv2_fpnlite_320x320_pp.rpk",
    )
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--labels", type=str, default="assets/coco_labels.txt")
    return parser.parse_args()

def load_labels(path):
    with open(path, "r") as f:
        return [line.strip() for line in f.readlines()]

def ssd_postprocess(outputs, threshold):
    boxes, classes, scores, num_detections = outputs
    boxes = boxes[0]  # shape: (100, 4)
    classes = classes[0].astype(int)  # shape: (100,)
    scores = scores[0]  # shape: (100,)
    num = int(num_detections[0][0])  # shape: (1,)

    results = []
    for i in range(num):
        if scores[i] >= threshold:
            results.append((boxes[i], scores[i], classes[i]))
    return results

if __name__ == "__main__":
    args = get_args()

    imx500 = IMX500(args.model)
    intrinsics = imx500.network_intrinsics or NetworkIntrinsics()
    intrinsics.task = "object detection"

    labels = load_labels(args.labels)

    picam2 = Picamera2(imx500.camera_num)
    config = picam2.create_preview_configuration()
    picam2.start(config)

    while True:
        metadata = picam2.capture_metadata()
        outputs = imx500.get_outputs(metadata, add_batch=True)

        if outputs is None or len(outputs) != 4:
            print("Unexpected number of output tensors.")
            continue

        try:
            detections = ssd_postprocess(outputs, args.threshold)

            if len(detections) == 0:
                print("No objects detected.")
                continue

            for box, score, cls in detections:
                label = labels[cls] if cls < len(labels) else f"Class {cls}"
                print(f"Detected: {label}, Confidence: {score:.2f}, Box: {box}")

        except Exception as e:
            print(f"Post-processing error: {e}")
