#!/usr/bin/env python3
# verify_line.py
# Parse lines like: Set1:SMoist25.25:SMoistPerc2323:STemp232
# and forward the numeric values to append_line.append_line(...)

import re
from Codebase.append_line import append_line

# Regex: label immediately followed by number, fields separated by ':'
_PATTERN = re.compile(
    r'^\s*'
    r'Set(?P<set>\d+)'
    r'\s*:\s*SMoist(?P<smoist>-?\d+(?:\.\d+)?)'
    r'\s*:\s*SMoistPerc(?P<smoistperc>-?\d+(?:\.\d+)?)'
    r'\s*:\s*STemp(?P<stemp>-?\d+(?:\.\d+)?)'
    r'\s*$'
)

def verify_line(line: str):
    """
    Parse the incoming line. On success:
      - Calls append_line(set_num, s_moist, s_moist_perc, s_temp)
      - Returns ((set_num, s_moist, s_moist_perc, s_temp), True)

    On parse failure:
      - Prints a brief notice and returns (line, False)
    """
    m = _PATTERN.match(line)
    if not m:
        # You can comment this out if you’d rather be silent on bad lines
        print(f"[verify_line] Reject (bad format): {line}")
        return line, False

    set_num = int(m.group('set'))
    # Use float for generality; cast later if you prefer ints for perc/temp
    s_moist = float(m.group('smoist'))
    s_moist_perc = float(m.group('smoistperc'))
    s_temp = float(m.group('stemp'))

    # Hand off to your append function
    append_line(set_num, s_moist, s_moist_perc, s_temp)

    return (set_num, s_moist, s_moist_perc, s_temp), True
