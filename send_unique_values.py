import dbus
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib
import argparse
from picamera2 import Picamera2
from picamera2.devices import IMX500
from picamera2.devices.imx500 import NetworkIntrinsics
import threading
import time

BLUEZ_SERVICE_NAME = 'org.bluez'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'

MAIN_LOOP = None

# GATT Characteristic
class ObjectDetectorCharacteristic(dbus.service.Object):
    PATH = '/org/bluez/example/service0/char0'
    UUID = '12345678-1234-5678-1234-56789abcdef1'

    def __init__(self, bus):
        self.value = []
        self.notifying = False
        self.bus = bus
        dbus.service.Object.__init__(self, bus, self.PATH)

    @dbus.service.method("org.bluez.GattCharacteristic1", in_signature='', out_signature='ay')
    def ReadValue(self):
        print("[GATT] Read request")
        return self.value

    @dbus.service.method("org.bluez.GattCharacteristic1", in_signature='', out_signature='')
    def StartNotify(self):
        self.notifying = True
        print("[GATT] Notifying started")

    @dbus.service.method("org.bluez.GattCharacteristic1", in_signature='', out_signature='')
    def StopNotify(self):
        self.notifying = False
        print("[GATT] Notifying stopped")

    def update_value(self, text):
        print(f"[DEBUG] Updating BLE value to: {text}")
        encoded = text.encode('utf-8')
        self.value = dbus.Array([dbus.Byte(b) for b in encoded], signature='y')
        if self.notifying:
            self.PropertiesChanged("org.bluez.GattCharacteristic1", {"Value": self.value}, [])

    @dbus.service.signal("org.freedesktop.DBus.Properties", signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass

# GATT Service
class ObjectDetectionService(dbus.service.Object):
    PATH = '/org/bluez/example/service0'
    UUID = '12345678-1234-5678-1234-56789abcdef0'

    def __init__(self, bus):
        dbus.service.Object.__init__(self, bus, self.PATH)
        self.char = ObjectDetectorCharacteristic(bus)

# GATT Application
class Application(dbus.service.Object):
    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)
        service = ObjectDetectionService(bus)
        self.services.append(service)
        self.services.append(service.char)

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        managed_objects = {}
        for service in self.services:
            if 'char0' in service.PATH:
                managed_objects[service.PATH] = {
                    'org.bluez.GattCharacteristic1': {
                        'UUID': service.UUID,
                        'Service': dbus.ObjectPath('/org/bluez/example/service0'),
                        'Flags': ['read', 'notify']
                    }
                }
            else:
                managed_objects[service.PATH] = {
                    'org.bluez.GattService1': {
                        'UUID': service.UUID,
                        'Primary': True
                    }
                }
        return managed_objects

# BLE Advertisement
class Advertisement(dbus.service.Object):
    PATH = '/org/bluez/example/advertisement0'

    def __init__(self, bus):
        self.bus = bus
        dbus.service.Object.__init__(self, bus, self.PATH)

    @dbus.service.method('org.freedesktop.DBus.Properties', in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        return {
            'Type': 'peripheral',
            'LocalName': 'picam',
            'ServiceUUIDs': dbus.Array(['12345678-1234-5678-1234-56789abcdef0'], signature='s'),
            'IncludeTxPower': dbus.Boolean(True)
        }

    @dbus.service.method('org.bluez.LEAdvertisement1', in_signature='', out_signature='')
    def Release(self):
        print('[BLE] Advertisement released')

def register_app(bus, app):
    adapter = find_adapter()
    service_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter), GATT_MANAGER_IFACE)
    service_manager.RegisterApplication(app.path, {}, reply_handler=lambda: print("GATT app registered"),
                                        error_handler=lambda e: print("Failed to register app:", str(e)))

def register_advertisement(bus, adv):
    adapter = find_adapter()
    ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter), LE_ADVERTISING_MANAGER_IFACE)
    ad_manager.RegisterAdvertisement(adv.PATH, {}, reply_handler=lambda: print("Advertisement registered"),
                                     error_handler=lambda e: print("Failed to register advertisement:", str(e)))

def find_adapter():
    bus = dbus.SystemBus()
    om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, "/"), DBUS_OM_IFACE)
    objects = om.GetManagedObjects()
    for path, interfaces in objects.items():
        if GATT_MANAGER_IFACE in interfaces:
            return path
    raise Exception("GATT Manager interface not found")

def start_object_detection(char: ObjectDetectorCharacteristic):
    print("[INFO] Starting object detection using Picamera2 + IMX500")

    model_path = "/usr/share/imx500-models/imx500_network_ssd_mobilenetv2_fpnlite_320x320_pp.rpk"
    labels_path = "coco_labels.txt"
    threshold = 0.3

    imx500 = IMX500(model_path)
    intrinsics = imx500.network_intrinsics or NetworkIntrinsics()
    intrinsics.task = "object detection"
    labels = load_labels(labels_path)
    print(f"[DEBUG] Loaded labels: {labels}")

    picam2 = Picamera2(imx500.camera_num)
    config = picam2.create_preview_configuration()
    picam2.start(config)

    last_label_str = None

    while True:
        metadata = picam2.capture_metadata()
        outputs = imx500.get_outputs(metadata, add_batch=True)
        print(f"[DEBUG] Raw outputs: {outputs}")

        if outputs is None or len(outputs) != 4:
            print("[WARN] Invalid outputs from model")
            continue

        try:
            detections = ssd_postprocess(outputs, threshold)
            print(f"[DEBUG] Processed detections: {detections}")

            if not detections:
                current_label_str = "No objects detected"
            else:
                detected_labels = []
                for box, score, cls in detections:
                    print(f"[DEBUG] Class index: {cls}, score: {score}, box: {box}")
                    label = labels[cls] if cls < len(labels) else f"Class {cls}"
                    print(f"[DEBUG] Detected label: {label}")
                    detected_labels.append(label)

                unique_sorted_labels = sorted(set(detected_labels))
                current_label_str = ", ".join(unique_sorted_labels)
                print(f"[DEBUG] Current unique label string: {current_label_str}")

            if current_label_str != last_label_str:
                print(f"[BLE] Sending update: {current_label_str}")
                char.update_value(current_label_str)
                last_label_str = current_label_str

        except Exception as e:
            print(f"[ERROR] Detection error: {e}")

        time.sleep(1)

def load_labels(path):
    print(f"[INFO] Loading labels from: {path}")
    with open(path, "r") as f:
        labels = [line.strip() for line in f.readlines()]
    print(f"[INFO] Loaded {len(labels)} labels")
    return labels

# Test comment
def ssd_postprocess(outputs, threshold):
    boxes, classes, scores, num_detections = outputs
    boxes = boxes[0]
    print(f"[DEBUG] classes[0]: {classes[0]}")
    classes = classes[0].astype(int)
    print(f"[DEBUG] classes: {classes}")
    scores = scores[0]
    num = int(num_detections[0][0])
    results = []
    for i in range(num):
        if scores[i] >= threshold:
            results.append((boxes[i], scores[i], classes[i]))
    return results

def main():
    global MAIN_LOOP
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    app = Application(bus)
    adv = Advertisement(bus)

    register_app(bus, app)
    register_advertisement(bus, adv)

    MAIN_LOOP = GLib.MainLoop()
    GLib.timeout_add(100, lambda: True)

    threading.Thread(target=start_object_detection, args=(app.services[1],), daemon=True).start()

    MAIN_LOOP.run()

if __name__ == '__main__':
    main()
