import subprocess
import json
import threading

# Shared variable to hold latest objects
latest_objects = []

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
            print(line.strip())  # View raw output for debugging

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
                        # Update shared data with latest detection
                        latest_objects = new_objects
                except json.JSONDecodeError:
                    pass

    except KeyboardInterrupt:
        process.terminate()
