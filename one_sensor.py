import smbus2
import time

I2C_ADDR = 0x10
bus = smbus2.SMBus(1)

def read_raw():
    try:
        while True:
            try:
                data = bus.read_i2c_block_data(I2C_ADDR, 0, 9)
                print("Raw:", [f"0x{b:02X}" for b in data])
                
                if data[0] == 0x59 and data[1] == 0x59:
                    distance = data[2] + (data[3] << 8)
                    print(f"✅ Valid data: {distance} cm")
                else:
                    print("⚠️ Invalid header")

            except OSError as e:
                print("❌ I2C read error:", e)

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("Stopped.")

read_raw()
