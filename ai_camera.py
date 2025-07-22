import subprocess
import json
import threading
import time

# Shared variable to hold latest objects
latest_objects = []

# Function to run object detection
def run_object_detection():
    global latest_objects

    command = [
        "rpicam-hello",
        "-t", "0s",
        "--post-process-file", "/usr/share/rpi-camera-assets/imx500_mobilenet_ssd.json",
        "--viewfinder-width", "1920",
        "--viewfinder-height", "1080",
        "--framerate", "30"
    ]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    try:
        for line in process.stdout:
            print(line.strip())  # Optional: print raw output

            if '"objects":' in line:
                try:
                    data = json.loads(line.strip())
                    if "objects" in data:
                        new_objects = []
                        for obj in data["objects"]:
                            label = obj.get("label")
                            confidence = obj.get("confidence", 0)
                            if label:
                                new_objects.append({"label": label, "confidence": confidence})
                        # Update shared variable with new detection results
                        latest_objects = new_objects
                except json.JSONDecodeError:
                    pass

    except KeyboardInterrupt:
        process.terminate()

# Function to print latest detected objects every 5 seconds
def print_latest_objects():
    global latest_objects
    while True:
        print("\nCurrent detected objects:")
        for obj in latest_objects:
            print(f"{obj['label']} (confidence: {obj['confidence']:.2f})")
        time.sleep(5)

# Start the detection in a background thread
detection_thread = threading.Thread(target=run_object_detection)
detection_thread.start()

# Start the print thread to monitor object detection
printer_thread = threading.Thread(target=print_latest_objects, daemon=True)
printer_thread.start()

# Keep the main thread alive so both threads keep running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping...")
