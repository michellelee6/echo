import argparse
from picamera2 import Picamera2
from picamera2.devices import IMX500
from picamera2.devices.imx500 import postprocess_nanodet_detection, NetworkIntrinsics

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        type=str,
        default="/usr/share/imx500-models/imx500_network_ssd_mobilenetv2_fpnlite_320x320_pp.rpk",
    )
    parser.add_argument("--threshold", type=float, default=0.55)
    parser.add_argument("--iou", type=float, default=0.65)
    parser.add_argument("--max-detections", type=int, default=10)
    parser.add_argument("--labels", type=str, default="assets/coco_labels.txt")
    return parser.parse_args()

def load_labels(path):
    with open(path, "r") as f:
        return [line.strip() for line in f.readlines()]

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

        if outputs is None or len(outputs) < 3:
            continue

        # Debug: print shapes of all outputs
        for i, output in enumerate(outputs):
            print(f"Output {i} shape: {output.shape}")

        try:
            detections = postprocess_nanodet_detection(
                outputs=outputs,
                conf=args.threshold,
                iou_thres=args.iou,
                max_out_dets=args.max_detections,
            )

            print("Detections output type:", type(detections))
            print("Detections output repr:", repr(detections))

            # Assuming detections is a tuple/list of (boxes, scores, classes)
            boxes, scores, classes = detections

            if len(boxes) > 0:
                for box, score, cls in zip(boxes, scores, classes):
                    label = labels[int(cls)] if int(cls) < len(labels) else f"Class {int(cls)}"
                    print(f"Detected: {label}, Confidence: {score:.2f}")

        except Exception as e:
            print(f"Post-processing error: {e}")
