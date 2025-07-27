from picamera2 import Picamera2
import time

# Initialize camera with IMX500 sensor (automatically uses imx500_mobilenet_ssd.json)
picam2 = Picamera2()

# Use full resolution preview configuration (adjust if needed)
config = picam2.create_preview_configuration(
    main={"size": (1920, 1080)},
    queue=True
)

picam2.configure(config)
picam2.start_preview()
picam2.start()

print("Camera started. Detecting objects...")

try:
    while True:
        metadata = picam2.capture_metadata()
        if "Objects" in metadata:
            for obj in metadata["Objects"]:
                label = obj.get("label", "Unknown")
                confidence = obj.get("confidence", 0)
                box = obj.get("box", [])
                print(f"Detected: {label} ({confidence:.2f}) at {box}")
        time.sleep(0.2)

except KeyboardInterrupt:
    print("Exiting...")
    picam2.stop()
