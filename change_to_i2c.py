from smbus2 import SMBus
import time

OLD_ADDR = 0x10  # current address
NEW_ADDR = 0x11  # desired new address (must be 0x01–0x7F)

def calculate_checksum(data):
    return sum(data) & 0xFF

def change_tfluna_i2c_address(old_addr, new_addr):
    with SMBus(1) as bus:
        # Build command frame
        frame = [
            0x5A,       # Header
            0x05,       # Function: write
            0x03,       # Data length
            0x11,       # Register: I2C address
            new_addr,   # New address to assign
            0x01        # Save to EEPROM
        ]
        frame.append(calculate_checksum(frame))  # Add checksum

        try:
            # Send full frame to register 0x00
            bus.write_i2c_block_data(old_addr, 0x00, frame)
            print(f"Sent address change to 0x{new_addr:02X}. Now power cycle the sensor.")
        except Exception as e:
            print("I2C command failed:", e)

change_tfluna_i2c_address(OLD_ADDR, NEW_ADDR)
