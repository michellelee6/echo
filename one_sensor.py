import time
from smbus2 import SMBus

I2C_ADDR = 0x10  # TF-Luna default I2C address

# Commands
ENABLE_OUTPUT_CMD = [0x5A, 0x05, 0x07, 0x01, 0x65]  # Enable measurement output
SAVE_SETTINGS_CMD = [0x5A, 0x04, 0x11, 0x6F]        # Save settings to flash

def send_command(command):
    with SMBus(1) as bus:
        try:
            bus.write_i2c_block_data(I2C_ADDR, 0x00, command)
            print("Command sent:", command)
            time.sleep(0.1)
        except Exception as e:
            print("Failed to send command:", e)

def read_distance():
    with SMBus(1) as bus:
        try:
            data = bus.read_i2c_block_data(I2C_ADDR, 0x00, 9)
            print("Raw data:", data)

            if data[0] == 0x59 and data[1] == 0x59:
                distance = data[2] + (data[3] << 8)  # cm
                strength = data[4] + (data[5] << 8)
                return distance, strength
            else:
                print(f"Bad header: {data[0]} {data[1]}")
                return None, None
        except Exception as e:
            print("Read failed:", e)
            return None, None

# --- MAIN SCRIPT ---
if __name__ == "__main__":
    print("Sending enable output command...")
    send_command(ENABLE_OUTPUT_CMD)

    # Optional: Save settings permanently (run once, then comment out)
    # print("Saving settings to flash...")
    # send_command(SAVE_SETTINGS_CMD)

    print("Starting distance readings...")
    time.sleep(0.5)

    while True:
        dist, strength = read_distance()
        if dist is not None:
            print(f"Distance: {dist} cm | Strength: {strength}")
        else:
            print("Invalid data")
        time.sleep(0.1)
