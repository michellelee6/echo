import dbus
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib
import time
import signal
import smbus2

# Bluetooth + DBus constants
BLUEZ_SERVICE_NAME = 'org.bluez'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
AD_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
ADAPTER_PATH = '/org/bluez/hci0'

# UUIDs (must match iOS)
SERVICE_UUID = '12345678-1234-5678-1234-56789ABCDEF0'
CHAR_UUID = '12345678-1234-5678-1234-56789ABCDEF1'

# Sensor I2C setup
SENSOR_ADDRESSES = [0x12, 0x13, 0x14]
bus = smbus2.SMBus(1)

# --------- Advertisement ---------
class Advertisement(dbus.service.Object):
    PATH = '/org/bluez/example/advertisement0'

    def __init__(self, bus):
        self.bus = bus
        dbus.service.Object.__init__(self, bus, self.PATH)

    def get_properties(self):
        return {
            'org.bluez.LEAdvertisement1': {
                'Type': 'peripheral',
                'ServiceUUIDs': [SERVICE_UUID],
                'LocalName': 'TF-Luna-Pi',
                'IncludeTxPower': True
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.PATH)

    @dbus.service.method('org.freedesktop.DBus.Properties', in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        return self.get_properties().get(interface, {})

    @dbus.service.method('org.bluez.LEAdvertisement1', in_signature='', out_signature='')
    def Release(self):
        print("Advertisement released")

# --------- GATT Characteristic ---------
class DistanceCharacteristic(dbus.service.Object):
    def __init__(self, bus, index, service):
        self.path = service.path + f'/char{index}'
        self.bus = bus
        self.value = [dbus.Byte(0)]
        self.notifying = True
        self.service = service
        dbus.service.Object.__init__(self, bus, self.path)

        self.start_notify_loop()

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method('org.freedesktop.DBus.Properties', in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != 'org.bluez.GattCharacteristic1':
            return {}
        return {
            'UUID': CHAR_UUID,
            'Service': self.service.get_path(),
            'Value': self.value,
            'Flags': ['read', 'notify']
        }

    @dbus.service.method('org.bluez.GattCharacteristic1', in_signature='a{sv}', out_signature='ay')
    def ReadValue(self, options):
        print("ReadValue called")
        self.update_sensor_value()
        return self.value

    # D-Bus signal to notify clients
    @dbus.service.signal('org.freedesktop.DBus.Properties', signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass

    def start_notify_loop(self):
        def notify_cb():
            if self.notifying:
                self.notify()
            return True  # continue calling
        GLib.timeout_add_seconds(1, notify_cb)

    def notify(self):
        self.update_sensor_value()
        self.PropertiesChanged(
            'org.bluez.GattCharacteristic1',
            {'Value': self.value},
            []
        )
        print("🔔 Notifying with value:", self.value)

    def update_sensor_value(self):
        readings = []
        for addr in SENSOR_ADDRESSES:
            try:
                data = bus.read_i2c_block_data(addr, 0, 2)
                dist = data[0] + (data[1] << 8)
                readings.append(str(dist))
            except Exception as e:
                print(f"Error reading from 0x{addr:02X}: {e}")
                readings.append("ERR")

        distance_string = ",".join(readings)
        print("Updated BLE characteristic with:", distance_string)

        self.value = dbus.Array(
            [dbus.Byte(b) for b in distance_string.encode('utf-8')],
            signature=dbus.Signature('y')
        )

# --------- GATT Service ---------
class DistanceService(dbus.service.Object):
    PATH_BASE = '/org/bluez/example/service'

    def __init__(self, bus, index):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)
        self.characteristics.append(DistanceCharacteristic(bus, 0, self))

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method('org.freedesktop.DBus.Properties', in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != 'org.bluez.GattService1':
            return {}
        return {
            'UUID': SERVICE_UUID,
            'Primary': True
        }

# --------- GATT Application ---------
class Application(dbus.service.Object):
    def __init__(self, bus):
        self.path = '/org/bluez/example/app'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)
        self.services.append(DistanceService(bus, 0))

    @dbus.service.method('org.freedesktop.DBus.ObjectManager', out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        managed_objects = {}
        for service in self.services:
            managed_objects[service.get_path()] = {
                'org.bluez.GattService1': service.GetAll('org.bluez.GattService1')
            }
            for char in service.characteristics:
                managed_objects[char.get_path()] = {
                    'org.bluez.GattCharacteristic1': char.GetAll('org.bluez.GattCharacteristic1')
                }
        return managed_objects

# --------- Main ---------
def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    adapter = bus.get_object(BLUEZ_SERVICE_NAME, ADAPTER_PATH)
    ad_manager = dbus.Interface(adapter, AD_MANAGER_IFACE)
    gatt_manager = dbus.Interface(adapter, GATT_MANAGER_IFACE)

    app = Application(bus)
    advert = Advertisement(bus)

    mainloop = GLib.MainLoop()

    def cleanup(*_):
        print("Cleaning up...")
        try:
            ad_manager.UnregisterAdvertisement(advert.get_path())
        except Exception as e:
            print("Failed to unregister advertisement:", e)
        mainloop.quit()

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    print("Registering GATT app and advertisement...")
    gatt_manager.RegisterApplication(app.path, {},
        reply_handler=lambda: print("✅ GATT app registered"),
        error_handler=lambda e: print(f"❌ Failed to register app: {e}"))

    ad_manager.RegisterAdvertisement(advert.get_path(), {},
        reply_handler=lambda: print("✅ Advertisement registered"),
        error_handler=lambda e: print(f"❌ Failed to register advert: {e}"))

    mainloop.run()

if __name__ == '__main__':
    main()
