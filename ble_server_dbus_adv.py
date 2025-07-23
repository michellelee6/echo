import dbus
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib
import subprocess
import json

BLUEZ_SERVICE_NAME = 'org.bluez'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'

MAIN_LOOP = None

class ObjectDetectorCharacteristic(dbus.service.Object):
    PATH = '/org/bluez/example/service0/char0'
    UUID = '12345678-1234-5678-1234-56789abcdef1'

    def __init__(self, bus):
        self.value = []
        self.notifying = False
        self.bus = bus
        dbus.service.Object.__init__(self, bus, self.PATH)

    @dbus.service.method("org.bluez.GattCharacteristic1",
                         in_signature='', out_signature='ay')
    def ReadValue(self):
        print("[GATT] Read request")
        return dbus.Array(self.value, signature='y')

    @dbus.service.method("org.bluez.GattCharacteristic1", in_signature='', out_signature='')
    def StartNotify(self):
        self.notifying = True
        print("[GATT] Notifying started")

    @dbus.service.method("org.bluez.GattCharacteristic1", in_signature='', out_signature='')
    def StopNotify(self):
        self.notifying = False
        print("[GATT] Notifying stopped")

    def update_value(self, text):
        self.value = [dbus.Byte(ord(c)) for c in text]
        if self.notifying:
            self.PropertiesChanged("org.bluez.GattCharacteristic1", {"Value": self.value}, [])

    @dbus.service.signal("org.freedesktop.DBus.Properties", signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass

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
            managed_objects[service.PATH] = {
                'org.bluez.GattService1': {
                    'UUID': service.UUID,
                    'Primary': True
                } if 'service0' in service.PATH else {
                    'UUID': service.UUID,
                    'Service': dbus.ObjectPath('/org/bluez/example/service0'),
                    'Flags': ['read', 'notify']
                }
            }
        return managed_objects

class Advertisement(dbus.service.Object):
    PATH = '/org/bluez/example/advertisement0'

    def __init__(self, bus):
        self.bus = bus
        dbus.service.Object.__init__(self, bus, self.PATH)

    @dbus.service.method('org.freedesktop.DBus.Properties',
                         in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        return {
            'Type': 'peripheral',
            'LocalName': 'PiCam',
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
    print("[INFO] Starting rpicam-hello object detection...")
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
                labels = [obj['label'] for obj in data.get('objects', [])]
                if labels:
                    print("Detected:", labels)
                    char.update_value(", ".join(labels))
            except Exception as e:
                print("[ERROR] Failed to parse:", e)

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
    from threading import Thread
    Thread(target=start_object_detection, args=(app.services[1],), daemon=True).start()
    MAIN_LOOP.run()

if __name__ == '__main__':
    main()
