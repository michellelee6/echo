from bluezero import peripheral
import time
import json
import subprocess

# Sample characteristic to send detected objects
class DetectionService:
    def __init__(self):
        self.detected_objects = []

        # Setup BLE peripheral
        self.ble_service = peripheral.Peripheral(adapter_addr='XX:XX:XX:XX:XX:XX',  # Replace with your Pi's Bluetooth MAC
                                                 local_name='PiDetection')
        self.ble_service.add_service(srv_id=1, uuid='12345678-1234-5678-1234-56789abcdef0', primary=True)
        self.ble_service.add_characteristic(srv_id=1,
                                            chr_id=1,
                                            uuid='12345678-1234-5678-1234-56789abcdef1',
                                            value='',
                                            notifying=True,
                                            flags=['read', 'notify'])

    def start(self):
        self.ble_service.start()
        print("BLE service started.")
        self.monitor_detections()

    def send_update(self, text):
        self.ble_service.update_characteristic_value(1, 1, text)

    def monitor_detections(self):
        print("Running object detection...")
        process = subprocess.Popen(
            ['rpicam-hello', '-t', '0s', '--post-process-file',
             '/usr/share/rpi-camera-assets/imx500_mobilenet_ssd.json',
             '--viewfinder-width', '1920', '--viewfinder-height', '1080', '--framerate', '30'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )

        for line in process.stdout:
            if "{" in line:
                try:
                    data = json.loads(line.strip())
                    objects = [obj['label'] for obj in data.get('objects', [])]
                    if objects:
                        msg = ', '.join(objects)
                        print("Detected:", msg)
                        self.send_update(msg)
                except Exception as e:
                    print("Parse error:", e)

if __name__ == '__main__':
    service = DetectionService()
    service.start()
