import subprocess
import json

# Command to run the AI model
command = [
    "rpicam-hello",
    "-t", "0s",
    "--post-process-file", "/usr/share/rpi-camera-assets/imx500_mobilenet_ssd.json",
    "--viewfinder-width", "1920",
    "--viewfinder-height", "1080",
    "--framerate", "30"
]

# Start process
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

# Process the output line by line
detected_objects = []

try:
    for line in process.stdout:
        print(line.strip())  # Optional: print to see raw output

        # Try to parse JSON if the output contains detection results
        if '"objects":' in line:
            try:
                data = json.loads(line.strip())
                if "objects" in data:
                    for obj in data["objects"]:
                        label = obj.get("label")
                        confidence = obj.get("confidence", 0)
                        if label:
                            detected_objects.append((label, confidence))
            except json.JSONDecodeError:
                pass

except KeyboardInterrupt:
    process.terminate()

# Print final list of detected objects
print("\nDetected objects:")
for obj in detected_objects:
    print(f"{obj[0]} (confidence: {obj[1]:.2f})")
