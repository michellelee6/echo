import argparse
import sys
import threading
import time
import os
from functools import lru_cache

import cv2
import numpy as np

import dbus
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib

from picamera2 import MappedArray, Picamera2
from picamera2.devices import IMX500
from picamera2.devices.imx500 import (NetworkIntrinsics,
                                      postprocess_nanodet_detection)

# ------------------------- Bluetooth Constants -------------------------
BLUEZ_SERVICE_NAME = 'org.bluez'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
AGENT_INTERFACE = 'org.bluez.Agent1'
AGENT_PATH = "/test/agent"

# ------------------------- Auto-Pairing Agent -------------------------
class AutoPairAgent(dbus.service.Object):
    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Release(self):
        print("[AGENT] Release")

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        print(f"[AGENT] RequestAuthorization for device {device}")
        return

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        print(f"[AGENT] RequestPinCode for device {device}")
        return "0000"

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        print(f"[AGENT] RequestPasskey for device {device}")
        return dbus.UInt32(123456)

    @dbus.service.method(AGENT_INTERFACE, in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device, passkey, entered):
        print(f"[AGENT] DisplayPasskey {passkey} entered {entered}")

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="")
    def RequestConfirmation(self, device):
        print(f"[AGENT] Auto-confirming pairing with {device}")
        return

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="")
    def AuthorizeService(self, device, uuid):
        print(f"[AGENT] AuthorizeService {uuid} on {device}")
        return

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Cancel(self):
        print("[AGENT] Cancel")

# ------------------------- GATT Characteristic -------------------------
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
        return self.value

    @dbus.service.method("org.bluez.GattCharacteristic1", in_signature='', out_signature='')
    def StartNotify(self):
        self.notifying = True

    @dbus.service.method("org.bluez.GattCharacteristic1", in_signature='', out_signature='')
    def StopNotify(self):
        self.notifying = False

    def update_value(self, text):
        encoded = text.encode('utf-8')
        self.value = dbus.Array([dbus.Byte(b) for b in encoded], signature='y')
        if self.notifying:
            self.PropertiesChanged("org.bluez.GattCharacteristic1", {"Value": self.value}, [])

    @dbus.service.signal("org.freedesktop.DBus.Properties", signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass

# ------------------------- GATT Service and App -------------------------
class ObjectDetectionService(dbus.service.Object):
    PATH = '/org/bluez/example/service0'
    UUID = '12345678-1234-5678-1234-56789abcdef0'

    def __init__(self, bus):
        dbus.service.Object.__init__(self, bus, self.PATH)
        self.char = ObjectDetectorCharacteristic(bus)

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

# ------------------------- Advertisement -------------------------
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

# ------------------------- Registration Helpers -------------------------
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

# ------------------------- Object Detection Thread -------------------------
last_detections = []
class Detection:
    def __init__(self, coords, category, conf, metadata):
        self.category = category
        self.conf = conf
        self.box = imx500.convert_inference_coords(coords, metadata, picam2)

def parse_detections(picam2, char: ObjectDetectorCharacteristic):
    while True:
        metadata = picam2.capture_metadata()
        global last_detections
        np_outputs = imx500.get_outputs(metadata, add_batch=True)
        input_w, input_h = imx500.get_input_size()
        if np_outputs is None:
            continue

        boxes, scores, classes = postprocess_nanodet_detection(outputs=np_outputs[0], conf=0.55, iou_thres=0.65, max_out_dets=10)[0]
        from picamera2.devices.imx500.postprocess import scale_boxes
        boxes = scale_boxes(boxes, 1, 1, input_h, input_w, False, False)

        last_detections = [
            Detection(box, category, score, metadata)
            for box, score, category in zip(boxes, scores, classes)
            if score > 0.55
        ]

        labels = ["person", "car", "dog"]  # Replace with actual labels if needed
        if last_detections:
            label = f"{labels[int(last_detections[0].category)]}"
            char.update_value(label)
        time.sleep(1)

# ------------------------- Main -------------------------
if __name__ == "__main__":
    os.system("bluetoothctl discoverable on")
    os.system("bluetoothctl pairable on")

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    agent = AutoPairAgent(bus, AGENT_PATH)
    manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez"), 'org.bluez.AgentManager1')
    manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput")
    manager.RequestDefaultAgent(AGENT_PATH)
    print("[AGENT] Auto-pairing agent registered")

    app = Application(bus)
    adv = Advertisement(bus)
    register_app(bus, app)
    register_advertisement(bus, adv)

    imx500 = IMX500("/usr/share/imx500-models/imx500_network_ssd_mobilenetv2_fpnlite_320x320_pp.rpk")
    intrinsics = imx500.network_intrinsics or NetworkIntrinsics()
    picam2 = Picamera2(imx500.camera_num)
    config = picam2.create_preview_configuration(controls={"FrameRate": intrinsics.inference_rate}, buffer_count=12)
    picam2.start(config, show_preview=True)

    threading.Thread(target=parse_detections, args=(picam2, app.services[1]), daemon=True).start()

    MAIN_LOOP = GLib.MainLoop()
    MAIN_LOOP.run()
