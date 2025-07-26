import dbus
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib

BLUEZ_SERVICE_NAME = 'org.bluez'
ADAPTER_IFACE = 'org.bluez.Adapter1'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
ADVERTisement_IFACE = 'org.bluez.LEAdvertisement1'

UUID = '12345678-1234-5678-1234-56789ABCDEF0'

class Advertisement(dbus.service.Object):
    PATH_BASE = '/org/bluez/example/advertisement'

    def __init__(self, bus, index):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            ADVERTisement_IFACE: {
                'Type': 'peripheral',
                'ServiceUUIDs': [UUID],
                'LocalName': 'TestBLEDevice',
                'IncludeTxPower': True
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(dbus_interface='org.freedesktop.DBus.Properties',
                         in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        return self.get_properties()[interface]

    @dbus.service.method(ADVERTisement_IFACE, in_signature='', out_signature='')
    def Release(self):
        print("Advertisement released")


def find_adapter(bus):
    obj = bus.get_object(BLUEZ_SERVICE_NAME, '/org/bluez/hci0')
    adapter_props = dbus.Interface(obj, 'org.freedesktop.DBus.Properties')
    return obj, adapter_props


def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    adapter_obj, adapter_props = find_adapter(bus)

    ad_manager = dbus.Interface(adapter_obj, LE_ADVERTISING_MANAGER_IFACE)

    advert = Advertisement(bus, 0)
    ad_manager.RegisterAdvertisement(advert.get_path(), {},
                                     reply_handler=lambda: print("Advertisement registered"),
                                     error_handler=lambda e: print(f"Failed to register: {e}"))

    mainloop = GLib.MainLoop()
    try:
        mainloop.run()
    except KeyboardInterrupt:
        print("Stopping advertisement...")
        ad_manager.UnregisterAdvertisement(advert)
        advert.remove_from_connection()


if __name__ == '__main__':
    main()
