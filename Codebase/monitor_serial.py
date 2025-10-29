#!/usr/bin/env python3
# monitor_serial.py
# Reads from a serial port and validates each line with verify_line.py logic

import sys
import time
import glob

from Codebase.append_line import append_line
from verify_line import verify_line
try:
    import serial
except ImportError:
    print("ERROR: pyserial not installed. Run: pip install pyserial")
    sys.exit(2)

DEFAULT_BAUD = 115200
PORT_GLOBS = ["/dev/ttyUSB*", "/dev/ttyACM*"]  # common USB-serial patterns

def pick_port(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    for pat in PORT_GLOBS:
        ports = sorted(glob.glob(pat))
        if ports:
            return ports[-1]  # pick the last (often newest)
    return None

def main():
    # Optional args: port and baud
    port = sys.argv[1] if len(sys.argv) > 1 else None
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_BAUD

    port = pick_port(port)
    if not port:
        print("No USB serial port found (looked for /dev/ttyUSB* and /dev/ttyACM*).")
        sys.exit(1)

    print(f"[monitor_serial] Opening {port} @ {baud}...")
    with serial.Serial(port, baudrate=baud, timeout=1) as ser:
        while True:
            line = ser.readline().decode(errors="replace").strip()
            if not line:
                # optional
                time.sleep(0.01)
                continue
            line_item, state = verify_line(line)
            if state:
                append_line(line_item)

if __name__ == "__main__":
    main()
