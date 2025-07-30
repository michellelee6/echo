import smbus2
import time

MUX_ADDRESS = 0x70  # I2C address of TCA9548A multiplexer
bus = smbus2.SMBus(1)

def select_channel(channel):
    if 0 <= channel <= 7:
        bus.write_byte(MUX_ADDRESS, 1 << channel)
        time.sleep(0.1)
    else:
        raise ValueError("Channel must be between 0 and 7")

def scan_i2c_bus():
    devices = []
    for addr in range(0x03, 0x78):
        try:
            bus.write_quick(addr)
            devices.append(hex(addr))
        except OSError:
            continue
    return devices

def main():
    print("Scanning all TCA9548A channels (0–7)...\n")
    for channel in range(8):
        try:
            select_channel(channel)
            print(f"Channel {channel} active. Scanning...")
            devices = scan_i2c_bus()
            if devices:
                print(f"  Devices found: {devices}")
            else:
                print("  No devices found.")
        except Exception as e:
            print(f"Error on channel {channel}: {e}")
        print("-" * 40)
        time.sleep(0.2)

if __name__ == "__main__":
    main()
