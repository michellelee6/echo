from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput
import time

# Initialize the camera
picam2 = Picamera2()

# Set up the configuration with post-processing (object detection)
config = picam2.create_preview_configuration(
    main={"size": (1920, 1080)},
    queue=True,
    transform=0,
    post_process="imx500_mobilenet_ssd"
)

picam2.configure(config)
picam2.start_preview()
picam2.start()

print("Camera started. Detecting objects...\n")

try:
    while True:
        # Grab AI metadata
        metadata = picam2.capture_metadata()
        if "objects" in metadata:
            for obj in metadata["objects"]:
                label = obj.get("label", "Unknown")
                confidence = obj.get("confidence", 0)
                box = obj.get("box", [])
                print(f"Detected: {label} ({confidence:.2f}) at {box}")
        time.sleep(0.2)

except KeyboardInterrupt:
    print("Exiting...")
    picam2.stop()
