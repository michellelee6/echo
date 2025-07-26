from smbus2 import SMBus, i2c_msg

OLD_ADDR = 0x10
NEW_ADDR = 0x11

def calculate_checksum(data):
    return sum(data) & 0xFF

def set_tfluna_i2c_address(old_addr, new_addr):
    # Command to change address: 5A 05 03 11 [NEW_ADDR] 01 [CHECKSUM]
    payload = [
        0x5A,       # Header
        0x05,       # Function: write
        0x03,       # Data length
        0x11,       # Register: I2C address
        new_addr,   # New address
        0x01        # Save command
    ]
    payload.append(calculate_checksum(payload))

    try:
        with SMBus(1) as bus:
            msg = i2c_msg.write(old_addr, payload)
            bus.i2c_rdwr(msg)
            print(f"Sent address change to 0x{new_addr:02X}")
            print("⚠️ Now power cycle the sensor for the change to take effect.")
    except Exception as e:
        print("I2C command failed:", e)

set_tfluna_i2c_address(OLD_ADDR, NEW_ADDR)
