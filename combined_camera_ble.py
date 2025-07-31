# Combined script with preview off and print statements removed
# NOTE: Only core BLE and error-related prints remain

import argparse
import sys
import threading
import time
from functools import lru_cache

import cv2
import numpy as np

import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib

from picamera2 import MappedArray, Picamera2
from picamera2.devices import IMX500
from picamera2.devices.imx500 import (NetworkIntrinsics, postprocess_nanodet_detection)

############################################################
# Bluetooth Auto-Pairing Agent
############################################################

AGENT_PATH = "/test/agent"

class Rejected(dbus.DBusException):
    _dbus_error_name = "org.bluez.Error.Rejected"

class Agent(dbus.service.Object):
    @dbus.service.method("org.bluez.Agent1", in_signature="", out_signature="")
    def Release(self): pass

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="")
    def RequestAuthorization(self, device): return

    @dbus.service.method("org.bluez.Agent1", in_signature="os", out_signature="")
    def DisplayPinCode(self, device, pincode): pass

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        return "0000"

    @dbus.service.method("org.bluez.Agent1", in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey): return

    @dbus.service.method("org.bluez.Agent1", in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid): return

    @dbus.service.method("org.bluez.Agent1", in_signature="", out_signature="")
    def Cancel(self): pass

def register_agent(bus):
    obj = bus.get_object("org.bluez", "/org/bluez")
    manager = dbus.Interface(obj, "org.bluez.AgentManager1")
    agent = Agent(bus, AGENT_PATH)
    manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput")
    manager.RequestDefaultAgent(AGENT_PATH)

############################################################
# BLE GATT Definitions
############################################################

BLUEZ_SERVICE_NAME = 'org.bluez'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'

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
    def PropertiesChanged(self, interface, changed, invalidated): pass

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
        self.services.extend([service, service.char])

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        managed = {}
        for s in self.services:
            if 'char0' in s.PATH:
                managed[s.PATH] = {
                    'org.bluez.GattCharacteristic1': {
                        'UUID': s.UUID,
                        'Service': dbus.ObjectPath('/org/bluez/example/service0'),
                        'Flags': ['read', 'notify']
                    }
                }
            else:
                managed[s.PATH] = {
                    'org.bluez.GattService1': {
                        'UUID': s.UUID,
                        'Primary': True
                    }
                }
        return managed

class Advertisement(dbus.service.Object):
    PATH = '/org/bluez/example/advertisement0'

    def __init__(self, bus):
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
    def Release(self): pass

def register_app(bus, app):
    path = find_adapter()
    manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, path), GATT_MANAGER_IFACE)
    manager.RegisterApplication(app.path, {}, reply_handler=lambda: None,
                                error_handler=lambda e: print("GATT registration failed:", str(e)))

def register_advertisement(bus, adv):
    path = find_adapter()
    manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, path), LE_ADVERTISING_MANAGER_IFACE)
    manager.RegisterAdvertisement(adv.PATH, {}, reply_handler=lambda: None,
                                  error_handler=lambda e: print("Advertisement failed:", str(e)))

def find_adapter():
    bus = dbus.SystemBus()
    om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, "/"), DBUS_OM_IFACE)
    for path, interfaces in om.GetManagedObjects().items():
        if GATT_MANAGER_IFACE in interfaces:
            return path
    raise Exception("No Bluetooth adapter with GATT interface found")

############################################################
# Object Detection Section
############################################################

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
        threshold = args.threshold
        iou = args.iou
        max_detections = args.max_detections
        np_outputs = imx500.get_outputs(metadata, add_batch=True)
        input_w, input_h = imx500.get_input_size()
        if np_outputs is None:
            continue
        if intrinsics.postprocess == "nanodet":
            boxes, scores, classes = postprocess_nanodet_detection(outputs=np_outputs[0],
                conf=threshold, iou_thres=iou, max_out_dets=max_detections)[0]
            from picamera2.devices.imx500.postprocess import scale_boxes
            boxes = scale_boxes(boxes, 1, 1, input_h, input_w, False, False)
        else:
            boxes, scores, classes = np_outputs[0][0], np_outputs[1][0], np_outputs[2][0]
            if intrinsics.bbox_normalization:
                boxes /= input_h
            if intrinsics.bbox_order == "xy":
                boxes = boxes[:, [1, 0, 3, 2]]
            boxes = np.array_split(boxes, 4, axis=1)
            boxes = zip(*boxes)

        last_detections = [Detection(box, cat, score, metadata) for box, score, cat in zip(boxes, scores, classes) if score > threshold]

        labels = get_labels()
        if last_detections:
            label = f"{labels[int(last_detections[0].category)]}"
            char.update_value(label)
        time.sleep(1)

@lru_cache
def get_labels():
    labels = intrinsics.labels
    if intrinsics.ignore_dash_labels:
        labels = [l for l in labels if l and l != "-"]
    return labels

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="/usr/share/imx500-models/imx500_network_ssd_mobilenetv2_fpnlite_320x320_pp.rpk")
    parser.add_argument("--threshold", type=float, default=0.55)
    parser.add_argument("--iou", type=float, default=0.65)
    parser.add_argument("--max-detections", type=int, default=10)
    parser.add_argument("--postprocess", choices=["", "nanodet"], default=None)
    parser.add_argument("--bbox-order", choices=["yx", "xy"], default="yx")
    parser.add_argument("--bbox-normalization", action=argparse.BooleanOptionalAction)
    parser.add_argument("--ignore-dash-labels", action=argparse.BooleanOptionalAction)
    parser.add_argument("--labels", type=str)
    parser.add_argument("--print-intrinsics", action="store_true")
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    register_agent(bus)

    app = Application(bus)
    adv = Advertisement(bus)
    register_app(bus, app)
    register_advertisement(bus, adv)

    imx500 = IMX500(args.model)
    intrinsics = imx500.network_intrinsics or NetworkIntrinsics()
    for key, val in vars(args).items():
        if key == 'labels' and val:
            with open(val, 'r') as f:
                intrinsics.labels = f.read().splitlines()
        elif hasattr(intrinsics, key) and val is not None:
            setattr(intrinsics, key, val)

    if intrinsics.labels is None:
        with open("assets/coco_labels.txt", "r") as f:
            intrinsics.labels = f.read().splitlines()
    if args.print_intrinsics:
        print(intrinsics)
        sys.exit()

    picam2 = Picamera2(imx500.camera_num)
    config = picam2.create_preview_configuration(controls={"FrameRate": intrinsics.inference_rate}, buffer_count=12)
    picam2.start(config, show_preview=False)  # PREVIEW DISABLED
    if intrinsics.preserve_aspect_ratio:
        imx500.set_auto_aspect_ratio()

    threading.Thread(target=parse_detections, args=(picam2, app.services[1]), daemon=True).start()

    GLib.MainLoop().run()
