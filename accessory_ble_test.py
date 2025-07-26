import dbus
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib
import time
import signal
import sys

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
        print(f"GetAll called for interface: {interface}")
        return self.get_properties()[interface]

    @dbus.service.method(ADVERT_IFACE, in_signature='', out_signature='')
    def Release(self):
        print("Advertisement released")

def restart_adapter():
    import subprocess
    print("Restarting bluetooth adapter hci0")
    subprocess.run(["sudo", "hciconfig", "hci0", "down"])
    time.sleep(1)
    subprocess.run(["sudo", "hciconfig", "hci0", "up"])
    print("Adapter reset complete")

def register_advertisement(bus, ad_manager, advert):
    try:
        ad_manager.RegisterAdvertisement(advert.get_path(), {},
                                         reply_handler=lambda: print("✅ Advertisement registered"),
                                         error_handler=lambda e: print(f"❌ Failed to register: {e}"))
    except Exception as e:
        print(f"Exception while registering advertisement: {e}")

def unregister_advertisement(ad_manager, advert):
    try:
        print("Attempting to unregister advertisement...")
        ad_manager.UnregisterAdvertisement(advert.get_path())
        print("Advertisement unregistered successfully")
    except Exception as e:
        print(f"Failed to unregister advertisement: {e}")

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    adapter_obj = bus.get_object(BLUEZ_SERVICE_NAME, ADAPTER_PATH)
    ad_manager = dbus.Interface(adapter_obj, AD_MANAGER_IFACE)

    advert = Advertisement(bus)

    restart_adapter()

    def advertise_loop():
        unregister_advertisement(ad_manager, advert)
        register_advertisement(bus, ad_manager, advert)
        return True  # repeat every 15 seconds

    GLib.timeout_add_seconds(15, advertise_loop)
    advertise_loop()

    def exit_gracefully(signum, frame):
        print("\nSignal received, cleaning up...")
        unregister_advertisement(ad_manager, advert)
        sys.exit(0)

    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)

    print("Starting main loop for BLE advertising...")
    try:
        GLib.MainLoop().run()
    except Exception as e:
        print(f"Exception in main loop: {e}")

if __name__ == '__main__':
    main()
