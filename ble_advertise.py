import dbus
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib
import threading

BLUEZ_SERVICE_NAME = 'org.bluez'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
AGENT_INTERFACE = 'org.bluez.Agent1'
AGENT_PATH = "/test/agent"

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

    @dbus.service.method(AGENT_INTERFACE, in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        print(f"[AGENT] Auto-confirming pairing with {device}, passkey: {passkey}")
        return

    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        print(f"[AGENT] AuthorizeService {uuid} on {device}")
        return

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Cancel(self):
        print("[AGENT] Cancel")

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

def find_adapter(bus):
    om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, "/"), DBUS_OM_IFACE)
    objects = om.GetManagedObjects()
    for path, interfaces in objects.items():
        if GATT_MANAGER_IFACE in interfaces:
            return path
    raise Exception("GATT Manager interface not found")

def register_app(bus, app):
    adapter = find_adapter(bus)
    service_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter), GATT_MANAGER_IFACE)
    service_manager.RegisterApplication(app.path, {}, reply_handler=lambda: print("GATT app registered"),
                                        error_handler=lambda e: print("Failed to register app:", str(e)))

def register_advertisement(bus, adv):
    adapter = find_adapter(bus)
    ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter), LE_ADVERTISING_MANAGER_IFACE)
    ad_manager.RegisterAdvertisement(adv.PATH, {}, reply_handler=lambda: print("Advertisement registered"),
                                     error_handler=lambda e: print("Failed to register advertisement:", str(e)))

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    # Enable discoverable and pairable via bluetoothctl system commands
    import os
    os.system("bluetoothctl discoverable on")
    os.system("bluetoothctl pairable on")

    # Register auto-pairing agent
    agent = AutoPairAgent(bus, AGENT_PATH)
    manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez"), 'org.bluez.AgentManager1')
    manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput")
    manager.RequestDefaultAgent(AGENT_PATH)
    print("[AGENT] Auto-pairing agent registered")

    # Create GATT application and advertisement
    app = Application(bus)
    adv = Advertisement(bus)

    register_app(bus, app)
    register_advertisement(bus, adv)

    # Start the main loop
    mainloop = GLib.MainLoop()

    # Start a thread-safe interface to update the characteristic externally
    def updater():
        import time
        while True:
            # For demo: update with current time every 5 seconds
            import datetime
            now = datetime.datetime.now().strftime("%H:%M:%S")
            app.services[1].update_value(now)
            time.sleep(5)
    threading.Thread(target=updater, daemon=True).start()

    mainloop.run()

if __name__ == "__main__":
    main()
