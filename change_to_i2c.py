from smbus2 import SMBus
import time

OLD_ADDR = 0x10
NEW_ADDR = 0x11

def calculate_checksum(data):
    return sum(data) & 0xFF

def set_tfluna_i2c_address(old_addr, new_addr):
    with SMBus(1) as bus:
        # Build command frame
        payload = [
            0x5A,       # Header
            0x05,       # Function: write
            0x03,       # Data length
            0x11,       # Register: I2C address register
            new_addr,   # New I2C address
            0x01        # Save command
        ]
        checksum = calculate_checksum(payload)
        payload.append(checksum)

        # Send command
        try:
            write = bus.write_i2c_block_data(old_addr, payload[0], payload[1:])
            print(f"Sent address change to 0x{new_addr:02X}, now power cycle the sensor.")
        except Exception as e:
            print("I2C command failed:", e)

set_tfluna_i2c_address(OLD_ADDR, NEW_ADDR)
