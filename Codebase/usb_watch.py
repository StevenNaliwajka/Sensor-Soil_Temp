#!/usr/bin/env python3
# usb_watch.py
# Reads from a serial port and passes each line to verify_line.py

import sys
import time
import serial
from verify_line import verify_line   # import your verifier

DEFAULT_BAUD = 9600

def usage():
    print("Usage: usb_watch.py PORT [BAUD]")
    sys.exit(2)

def main():
    if len(sys.argv) < 2:
        usage()

    port = sys.argv[1]
    baud = DEFAULT_BAUD

    print(f"[usb_watch] Listening on {port} @ {baud}...")

    try:
        with serial.Serial(port, baudrate=baud, timeout=1) as ser:
            while True:
                line = ser.readline().decode(errors="replace").strip()
                if not line:
                    time.sleep(0.01)
                    continue

                # Send line to verify_line
                verify_line(line)

    except KeyboardInterrupt:
        print("\n[usb_watch] Stopped by user.")
    except Exception as e:
        print(f"[usb_watch] ERROR: {e}")

if __name__ == "__main__":
    main()
