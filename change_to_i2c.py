import smbus2
import time

# Original and new I2C addresses
OLD_ADDR = 0x10
NEW_ADDR = 0x11

# EEPROM address change command sequence for TF-Luna
# Format: [0x5A, 0x04, 0x11, new_addr, 0x00] + checksum
def build_command(new_addr):
    cmd = [0x5A, 0x04, 0x11, new_addr, 0x00]
    checksum = sum(cmd) & 0xFF
    cmd.append(checksum)
    return cmd

def change_address(bus, old_addr, new_addr):
    command = build_command(new_addr)
    print(f"Sending EEPROM change command to 0x{old_addr:02X} to set new address 0x{new_addr:02X}")
    try:
        bus.write_i2c_block_data(old_addr, command[0], command[1:])
        print("Command sent. Waiting 1 second...")
        time.sleep(1)
        print("Address change complete. Please power cycle the sensor.")
    except Exception as e:
        print("Failed to send command:", e)

if __name__ == "__main__":
    bus = smbus2.SMBus(1)  # Use I2C bus 1 on RPi
    change_address(bus, OLD_ADDR, NEW_ADDR)
    bus.close()
