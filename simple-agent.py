#!/usr/bin/env python3

import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib

AGENT_PATH = "/test/agent"

class Agent(dbus.service.Object):
    @dbus.service.method("org.bluez.Agent1", in_signature="", out_signature="")
    def Release(self):
        print("Agent Released")

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        print("RequestAuthorization", device)

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        print("RequestPinCode", device)
        return "0000"

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        print("RequestPasskey", device)
        return dbus.UInt32(123456)

    @dbus.service.method("org.bluez.Agent1", in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device, passkey, entered):
        print("DisplayPasskey", device, passkey, entered)

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="")
    def AuthorizeService(self, device, uuid):
        print("AuthorizeService", device, uuid)
        return

    @dbus.service.method("org.bluez.Agent1", in_signature="", out_signature="")
    def Cancel(self):
        print("Cancel")

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()
    path = "/test/agent"
    capability = "NoInputNoOutput"

    agent = Agent(bus, path)

    obj = bus.get_object("org.bluez", "/org/bluez")
    manager = dbus.Interface(obj, "org.bluez.AgentManager1")
    manager.RegisterAgent(path, capability)
    manager.RequestDefaultAgent(path)

    print("Agent registered")
    mainloop = GLib.MainLoop()
    mainloop.run()

if __name__ == "__main__":
    main()
