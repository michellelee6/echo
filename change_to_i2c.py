from smbus2 import SMBus
import time

OLD_ADDR = 0x10  # current address
NEW_ADDR = 0x11  # new address

# TF-Luna I2C register addresses
I2C_ADDR_REG = 0x11  # EEPROM address register
SAVE_REG = 0x20      # Save settings command register

def change_tfluna_address(old_addr, new_addr):
    with SMBus(1) as bus:
        try:
            # Write new I2C address to EEPROM address register
            bus.write_byte_data(old_addr, I2C_ADDR_REG, new_addr)
            time.sleep(0.1)

            # Save to EEPROM so it persists after reboot
            bus.write_byte_data(old_addr, SAVE_REG, 0x01)
            time.sleep(0.1)

            print(f"Address changed from 0x{old_addr:02X} to 0x{new_addr:02X}")
        except Exception as e:
            print("Failed to change address:", e)

change_tfluna_address(OLD_ADDR, NEW_ADDR)