#!/usr/bin/env python3
# usb_watch.py -- serial-focused watcher (polling)
import time
import glob
import subprocess
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
MONITOR = HERE / "monitor_serial.py"

PATTERNS = ["/dev/ttyUSB*", "/dev/ttyACM*"]
POLL_SEC = 1.0

def current_ttys() -> set[str]:
    out = set()
    for pat in PATTERNS:
        out.update(glob.glob(pat))
    return out

def main():
    print("[usb_watch] Watching for USB serial devices...")
    seen = current_ttys()
    try:
        while True:
            time.sleep(POLL_SEC)
            now = current_ttys()
            new = sorted(now - seen)
            if new:
                # pick the newest-looking device and launch monitor_serial.py
                port = new[-1]
                print(f"[usb_watch] Detected: {port}. Launching monitor_serial.py...")
                subprocess.Popen([sys.executable, str(MONITOR), port], cwd=str(HERE))
            seen = now
    except KeyboardInterrupt:
        print("\n[usb_watch] Exiting.")

if __name__ == "__main__":
    main()
