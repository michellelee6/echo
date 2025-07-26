import dbus
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib
import time

BLUEZ_SERVICE_NAME = 'org.bluez'
ADVERT_IFACE = 'org.bluez.LEAdvertisement1'
ADAPTER_PATH = '/org/bluez/hci0'
AD_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'

UUID = '12345678-1234-5678-1234-56789ABCDEF0'

class Advertisement(dbus.service.Object):
    PATH = '/org/bluez/example/advertisement0'

    def __init__(self, bus):
        self.bus = bus
        dbus.service.Object.__init__(self, bus, self.PATH)

    def get_properties(self):
        return {
            ADVERT_IFACE: {
                'Type': 'peripheral',
                'ServiceUUIDs': [UUID],
                'LocalName': 'TestBLEDevice',
                'IncludeTxPower': True
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.PATH)

    @dbus.service.method(dbus_interface='org.freedesktop.DBus.Properties',
                         in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        return self.get_properties()[interface]

    @dbus.service.method(ADVERT_IFACE, in_signature='', out_signature='')
    def Release(self):
        print("Advertisement released")


def restart_adapter():
    import subprocess
    subprocess.run(["sudo", "hciconfig", "hci0", "down"])
    time.sleep(1)
    subprocess.run(["sudo", "hciconfig", "hci0", "up"])
    print("Adapter reset")

def register_advertisement(bus, ad_manager, advert):
    try:
        ad_manager.RegisterAdvertisement(advert.get_path(), {},
                                         reply_handler=lambda: print("✅ Advertisement registered"),
                                         error_handler=lambda e: print(f"❌ Failed to register: {e}"))
    except Exception as e:
        print(f"Exception while registering: {e}")

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    adapter_obj = bus.get_object(BLUEZ_SERVICE_NAME, ADAPTER_PATH)
    ad_manager = dbus.Interface(adapter_obj, AD_MANAGER_IFACE)

    advert = Advertisement(bus)

    restart_adapter()

    # Attempt to register advertisement, retry every 10 seconds if failed
    def advertise_loop():
        try:
            ad_manager.UnregisterAdvertisement(advert.get_path())
            print("🔄 Unregistered old advertisement")
        except:
            pass  # In case not already registered

        register_advertisement(bus, ad_manager, advert)
        return True  # Repeat timer

    GLib.timeout_add_seconds(15, advertise_loop)
    advertise_loop()

    try:
        GLib.MainLoop().run()
    except KeyboardInterrupt:
        print("Interrupted by user")
        try:
            ad_manager.UnregisterAdvertisement(advert)
        except:
            pass

if __name__ == '__main__':
    main()
