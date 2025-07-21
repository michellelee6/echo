import dbus
import dbus.mainloop.glib
from gi.repository import GLib
import os

BLUEZ_SERVICE_NAME = 'org.bluez'
ADAPTER_IFACE = 'org.bluez.Adapter1'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
ADVERT_PATH = '/org/bluez/example/advertisement0'

class Advertisement(dbus.service.Object):
    PATH_BASE = '/org/bluez/example/advertisement'

    def __init__(self, bus, index):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            'Type': 'peripheral',
            'LocalName': 'MyPiBLE',
            'ServiceUUIDs': ['12345678-1234-5678-1234-56789abcdef0'],
            'Includes': ['tx-power']
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(dbus_interface='org.freedesktop.DBus.Properties',
                         in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        return self.get_properties()

    @dbus.service.method(dbus_interface='org.bluez.LEAdvertisement1',
                         in_signature='', out_signature='')
    def Release(self):
        print('Advertisement released')

def find_adapter(bus):
    obj_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                                 'org.freedesktop.DBus.ObjectManager')
    objects = obj_manager.GetManagedObjects()
    for path, ifaces in objects.items():
        if ADAPTER_IFACE in ifaces:
            return path
    return None

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    adapter_path = find_adapter(bus)
    if not adapter_path:
        print('Bluetooth adapter not found')
        return

    ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter_path),
                                LE_ADVERTISING_MANAGER_IFACE)

    advertisement = Advertisement(bus, 0)

    ad_manager.RegisterAdvertisement(advertisement.get_path(), {},
                                     reply_handler=lambda: print("Advertisement registered"),
                                     error_handler=lambda e: print(f"Failed to register: {e}"))

    try:
        GLib.MainLoop().run()
    except KeyboardInterrupt:
        print('Exiting')
        ad_manager.UnregisterAdvertisement(advertisement)
        advertisement.remove_from_connection(bus)

if __name__ == '__main__':
    main()
