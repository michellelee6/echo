from picamera2 import Picamera2
import time

picam2 = Picamera2()

config = picam2.create_preview_configuration(main={"size": (1920, 1080)})
picam2.configure(config)
picam2.start()
print("Camera started. Detecting objects...")

time.sleep(2)  # Give post-processing time to start

try:
    while True:
        metadata = picam2.capture_metadata()
        print("Metadata:", metadata)  # See what's being returned

        objects = metadata.get("Objects") or metadata.get("objects")
        if objects:
            for obj in objects:
                label = obj.get("label", "Unknown")
                confidence = obj.get("confidence", 0)
                box = obj.get("box", [])
                print(f"Detected: {label} ({confidence:.2f}) at {box}")
        time.sleep(0.2)

except KeyboardInterrupt:
    print("Exiting...")
    picam2.stop()