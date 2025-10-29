import serial
import time

from parse_line import parse_line

# --- Configuration ---
PORT = "/dev/ttyUSB0"
BAUDRATE = 9600
TIMEOUT = 1

def main():
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT) as ser:
            print(f"Listening on {PORT} at {BAUDRATE} baud...")
            while True:
                if ser.in_waiting > 0:
                    line = ser.readline().decode(errors='ignore').strip()
                    if line:
                        print(f"[{time.strftime('%H:%M:%S')}] {line}")
                        parsed_line = parse_line(line)
                        append_line(parsed_line)
                time.sleep(0.05)
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("\nExiting cleanly.")

if __name__ == "__main__":
    main()
