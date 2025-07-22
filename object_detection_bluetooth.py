import time
import numpy as np
from PIL import Image
import tflite_runtime.interpreter as tflite
from picamera2 import Picamera2
import bluetooth

# === Load TensorFlow Lite Model ===
interpreter = tflite.Interpreter(model_path="detect.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# === Initialize Camera ===
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (300, 300)}))
picam2.start()
time.sleep(2)

# === Setup Bluetooth Server ===
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]
bluetooth.advertise_service(server_sock, "ObjectDetectService",
                            service_classes=[bluetooth.SERIAL_PORT_CLASS],
                            profiles=[bluetooth.SERIAL_PORT_PROFILE])

print("Waiting for Bluetooth connection...")
client_sock, address = server_sock.accept()
print(f"Connected to {address}")

# === Helper Functions ===
def capture_frame():
    return picam2.capture_array()

def preprocess_frame(frame):
    img = Image.fromarray(frame).resize((300, 300))
    input_tensor = np.expand_dims(np.array(img), axis=0).astype(np.uint8)
    return input_tensor

def detect_objects(image):
    interpreter.set_tensor(input_details[0]['index'], image)
    interpreter.invoke()
    return interpreter.get_tensor(output_details[0]['index'])

def parse_detections(detections, threshold=0.5):
    # Output shape: [1, num_boxes, 4 or more]
    objects = []
    for det in detections[0]:
        class_id = int(det[0])
        confidence = det[1]
        if confidence > threshold:
            objects.append(f"Object ID {class_id} (Confidence: {confidence:.2f})")
    return objects

def send_to_mobile(labels):
    if labels:
        message = "\n".join(labels)
    else:
        message = "No objects detected"
    try:
        client_sock.send(message + "\n")
        print("Sent:", message)
    except:
        print("Bluetooth connection lost.")
        exit()

# === Main Loop ===
try:
    while True:
        frame = capture_frame()
        input_tensor = preprocess_frame(frame)
        detections = detect_objects(input_tensor)
        labels = parse_detections(detections)
        send_to_mobile(labels)
        time.sleep(1)  # Optional: reduce detection frequency

except KeyboardInterrupt:
    print("Exiting...")

finally:
    client_sock.close()
    server_sock.close()
    picam2.close()
