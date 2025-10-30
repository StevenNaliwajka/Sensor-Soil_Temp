#!/usr/bin/env python3
# monitor_serial.py
# Watch for a (new) USB-serial port; when one appears and opens, run usb_watch.py on it.
# If open fails due to EACCES, try to grant a temporary ACL with sudo (optional).
# If usb_watch.py exits, resume watching for a newer device.

import sys
import time
import glob
import os
import subprocess
import shlex

try:
    import serial
except ImportError:
    print("ERROR: pyserial not installed. Run: pip install pyserial")
    sys.exit(2)

DEFAULT_BAUD = int(os.environ.get("SERIAL_BAUD", "115200"))
SCAN_INTERVAL_SEC = float(os.environ.get("SERIAL_SCAN_INTERVAL", "0.25"))
# Set to 1 to allow the script to try a one-time sudo ACL fix on permission error.
ALLOW_SUDO_ACL = os.environ.get("SERIAL_ALLOW_SUDO_ACL", "1") == "1"

PORT_GLOBS = [
    "/dev/serial/by-id/*",  # stable names if present
    "/dev/ttyACM*",
    "/dev/ttyUSB*",
]

# Keep track so we don't re-run ACL fix repeatedly on the same device
_attempted_acl = set()


def list_ports():
    """Return list of (display_path, real_path, mtime), newest last."""
    seen_real = set()
    ports = []
    for pat in PORT_GLOBS:
        for p in glob.glob(pat):
            try:
                rp = os.path.realpath(p)
                if rp in seen_real:
                    continue
                st = os.stat(p)
                seen_real.add(rp)
                ports.append((p, rp, st.st_mtime))
            except (FileNotFoundError, PermissionError):
                continue
    ports.sort(key=lambda t: (t[2], t[0]))
    return ports


def newest_port_signature():
    ports = list_ports()
    return ports[-1] if ports else None  # (disp, real, mtime)


def _open_once(port, baud):
    """Try open once; return (ok: bool, exc: Exception|None)."""
    try:
        with serial.Serial(port, baudrate=baud, timeout=1) as s:
            _ = s.read(1)
        return True, None
    except Exception as e:
        return False, e


def _try_acl_fix(realnode: str) -> bool:
    """
    Try to grant a temporary ACL allowing the current user rw access:
      sudo setfacl -m u:$USER:rw <realnode>
    Only once per device path.
    """
    if realnode in _attempted_acl:
        return False
    _attempted_acl.add(realnode)

    if not ALLOW_SUDO_ACL:
        return False

    user = os.environ.get("USER") or os.environ.get("LOGNAME") or "root"
    cmd = ["sudo", "-n", "setfacl", "-m", f"u:{user}:rw", realnode]
    try:
        print(f"[monitor_serial] Attempting temporary ACL with: {' '.join(shlex.quote(c) for c in cmd)}")
        rc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).returncode
        if rc == 0:
            print("[monitor_serial] ACL granted; retrying open...")
            return True
        else:
            print("[monitor_serial] ACL attempt failed (no sudo or denied). "
                  f"Run manually:\n  sudo setfacl -m u:{user}:rw {realnode}")
            return False
    except FileNotFoundError:
        print("[monitor_serial] 'sudo' not found; cannot grant ACL automatically.")
        return False
    except Exception as e:
        print(f"[monitor_serial] ACL attempt error: {e}")
        return False


def can_open_with_self_heal(display_path: str, realnode: str, baud: int) -> bool:
    ok, err = _open_once(display_path, baud)
    if ok:
        return True

    # Inspect common root causes and try to help
    msg = str(err)
    if isinstance(err, PermissionError) or "Permission denied" in msg:
        print(f"[monitor_serial] Permission denied for {display_path} -> {realnode}")
        if _try_acl_fix(realnode):
            # retry once after ACL
            ok2, err2 = _open_once(display_path, baud)
            if ok2:
                return True
            print(f"[monitor_serial] Still cannot open after ACL: {err2}")
        else:
            # clear guidance (no spam)
            user = os.environ.get("USER") or os.environ.get("LOGNAME") or "root"
            print("  To allow access without replug/reboot (temporary until device replug):")
            print(f"    sudo setfacl -m u:{user}:rw {realnode}")
            print("  Permanent fix (persist across reboots/replugs): add your user to 'dialout' and/or add a udev rule.")
        time.sleep(2.0)
        return False

    if "Device or resource busy" in msg or "could not open port" in msg and "busy" in msg.lower():
        print(f"[monitor_serial] Device appears busy: {display_path} -> {realnode}")
        print("  Check if ModemManager/brltty is grabbing it:")
        print("    sudo systemctl stop ModemManager brltty 2>/dev/null || true")
        print("    sudo systemctl disable ModemManager brltty 2>/dev/null || true")
        print("  Also see which process has it: sudo fuser -v {realnode} || sudo lsof {realnode}")
        time.sleep(2.0)
        return False

    # generic failure
    print(f"[monitor_serial] Cannot open {display_path} @ {baud}: {err}")
    time.sleep(1.0)
    return False


def run_usb_watch(port: str, baud: int) -> int:
    cmd = [sys.executable, "usb_watch.py", port, str(baud)]
    print(f"[monitor_serial] Launching: {' '.join(shlex.quote(c) for c in cmd)}")
    try:
        completed = subprocess.run(cmd)
        rc = completed.returncode
        print(f"[monitor_serial] usb_watch.py exited with code {rc}")
        return rc
    except FileNotFoundError:
        print("[monitor_serial] ERROR: usb_watch.py not found next to this script.")
        return 127
    except Exception as e:
        print(f"[monitor_serial] ERROR running usb_watch.py: {e}")
        return 1


def main():
    # CLI:
    #   monitor_serial.py [baud]
    baud = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_BAUD

    print("[monitor_serial] Waiting for a USB serial device...")
    last_sig = None  # (display, real, mtime)

    try:
        while True:
            sig = newest_port_signature()
            if not sig:
                time.sleep(SCAN_INTERVAL_SEC)
                continue

            display_path, realnode, mtime = sig
            is_new = (last_sig is None
                      or display_path != last_sig[0]
                      or realnode != last_sig[1]
                      or mtime > last_sig[2])

            if not is_new:
                time.sleep(SCAN_INTERVAL_SEC)
                continue

            print(f"[monitor_serial] Candidate: {display_path} (-> {realnode}, mtime={mtime:.3f})")
            if not can_open_with_self_heal(display_path, realnode, baud):
                # couldn't open; keep scanning
                time.sleep(SCAN_INTERVAL_SEC)
                continue

            last_sig = (display_path, realnode, mtime)
            rc = run_usb_watch(display_path, baud)

            # Regardless of rc, resume watch for a newer device
            print("[monitor_serial] Resuming watch for next/newer USB serial device...")
            time.sleep(SCAN_INTERVAL_SEC)

    except KeyboardInterrupt:
        print("\n[monitor_serial] Stopped by user.")


if __name__ == "__main__":
    main()
