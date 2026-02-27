import time
import argparse
import sys
import threading

try:
    import serial
except ImportError:
    print("Error: 'pyserial' not found.")
    sys.exit(1)

def sender_loop(port, name, period, phase_shift):
    print(f"[{name}] Opening {port}...")
    try:
        ser = serial.Serial(port, 115200)
    except Exception as e:
        print(f"[{name}] Failed to open {port}: {e}")
        return

    t = 0
    import math

    print(f"[{name}] Sending data...")
    try:
        while True:
            # Generate sine wave position 0-9999
            val = (math.sin(t + phase_shift) + 1) / 2
            pos = int(val * 9999)

            # Send command
            cmd = f"L0{pos:04d} I10\n"
            ser.write(cmd.encode())

            time.sleep(0.02) # 50Hz
            t += 0.02 * (2 * math.pi / period)

    except KeyboardInterrupt:
        pass
    finally:
        ser.close()
        print(f"[{name}] Closed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate dual OSR devices sending T-Code.")
    parser.add_argument("port1", help="First COM port (e.g. COM1)")
    parser.add_argument("port2", help="Second COM port (e.g. COM2)")
    args = parser.parse_args()

    # Start two threads
    t1 = threading.Thread(target=sender_loop, args=(args.port1, "LEFT", 2.0, 0))
    t2 = threading.Thread(target=sender_loop, args=(args.port2, "RIGHT", 2.0, 3.14)) # 180 phase shift

    t1.start()
    t2.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
