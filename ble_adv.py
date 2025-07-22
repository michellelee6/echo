import dbus
import dbus.mainloop.glib
from gi.repository import GLib
import sys

BLUEZ_SERVICE_NAME = 'org.bluez'
ADAPTER_IFACE = 'org.bluez.Adapter1'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'

SERVICE_UUID = '12345678-1234-5678-1234-56789abcdef0'
CHAR_UUID = '12345678-1234-5678-1234-56789abcdef1'
LOCAL_NAME = 'MyPiBLE'

mainloop = None

class Advertisement(dbus.service.Object):
    PATH_BASE = '/org/bluez/example/advertisement'

    def __init__(self, bus, index):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            'org.bluez.LEAdvertisement1': {
                'Type': 'peripheral',
                'LocalName': LOCAL_NAME,
                'ServiceUUIDs': [SERVICE_UUID],
                'Includes': ['tx-power']
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method('org.freedesktop.DBus.Properties', 
                         in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != 'org.bluez.LEAdvertisement1':
            raise Exception('Invalid interface %s' % interface)
        return self.get_properties()['org.bluez.LEAdvertisement1']

    @dbus.service.method('org.bluez.LEAdvertisement1', in_signature='', out_signature='')
    def Release(self):
        print('Advertisement released')

class Application(dbus.service.Object):
    PATH_BASE = '/org/bluez/example/service'

    def __init__(self, bus):
        self.path = self.PATH_BASE
        self.bus = bus
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)
        self.add_service(TestService(bus, 0))

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            for char in service.get_characteristics():
                response[char.get_path()] = char.get_properties()
        return response

class Service(dbus.service.Object):
    def __init__(self, bus, index, uuid, primary):
        self.path = f'/org/bluez/example/service{index}'
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            'org.bluez.GattService1': {
                'UUID': self.uuid,
                'Primary': self.primary,
                'Characteristics': dbus.Array([char.get_path() for char in self.characteristics], signature='o')
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, characteristic):
        self.characteristics.append(characteristic)

    def get_characteristics(self):
        return self.characteristics

class Characteristic(dbus.service.Object):
    def __init__(self, bus, index, uuid, flags, service):
        self.path = service.get_path() + f'/char{index}'
        self.bus = bus
        self.uuid = uuid
        self.flags = flags
        self.service = service
        self.notifying = False
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            'org.bluez.GattCharacteristic1': {
                'Service': self.service.get_path(),
                'UUID': self.uuid,
                'Flags': self.flags
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    # Methods to override
    @dbus.service.method('org.bluez.GattCharacteristic1', in_signature='a{sv}', out_signature='ay')
    def ReadValue(self, options):
        print('Default ReadValue called, returning empty')
        return []

    @dbus.service.method('org.bluez.GattCharacteristic1', in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('Default WriteValue called, ignoring')

    @dbus.service.method('org.bluez.GattCharacteristic1')
    def StartNotify(self):
        print('Notifications enabled')
        self.notifying = True

    @dbus.service.method('org.bluez.GattCharacteristic1')
    def StopNotify(self):
        print('Notifications disabled')
        self.notifying = False

    def notify(self, value):
        if not self.notifying:
            return
        self.PropertiesChanged('org.bluez.GattCharacteristic1', {'Value': value}, [])

    @dbus.service.signal('org.freedesktop.DBus.Properties', signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass

class TestCharacteristic(Characteristic):
    def __init__(self, bus, index, uuid, flags, service):
        super().__init__(bus, index, uuid, flags, service)
        self.value = []

    def ReadValue(self, options):
        print('ReadValue called')
        return self.value

    def update_value(self, new_str):
        self.value = [dbus.Byte(c.encode()) for c in new_str]
        print(f'Value updated to: {new_str}')
        self.notify(self.value)

class TestService(Service):
    def __init__(self, bus, index):
        super().__init__(bus, index, SERVICE_UUID, True)
        self.test_char = TestCharacteristic(bus, 0, CHAR_UUID, ['read', 'notify'], self)
        self.add_characteristic(self.test_char)

def find_adapter(bus):
    obj_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                                 DBUS_OM_IFACE)
    objects = obj_manager.GetManagedObjects()
    for path, ifaces in objects.items():
        if ADAPTER_IFACE in ifaces:
            return path
    return None

def main():
    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    adapter_path = find_adapter(bus)
    if not adapter_path:
        print('Bluetooth adapter not found')
        return

    ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter_path),
                                LE_ADVERTISING_MANAGER_IFACE)
    gatt_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter_path),
                                  GATT_MANAGER_IFACE)

    advertisement = Advertisement(bus, 0)
    app = Application(bus)

    mainloop = GLib.MainLoop()

    # Register Advertisement
    ad_manager.RegisterAdvertisement(advertisement.get_path(), {},
                                     reply_handler=lambda: print("Advertisement registered"),
                                     error_handler=lambda e: print(f"Failed to register advertisement: {e}"))

    # Register GATT Application
    gatt_manager.RegisterApplication(app.get_path(), {},
                                     reply_handler=lambda: print("GATT application registered"),
                                     error_handler=lambda e: print(f"Failed to register application: {e}"))

    try:
        mainloop.run()
    except KeyboardInterrupt:
        print('Program interrupted')
        ad_manager.UnregisterAdvertisement(advertisement.get_path())
        gatt_manager.UnregisterApplication(app.get_path())
        mainloop.quit()

if __name__ == '__main__':
    main()
