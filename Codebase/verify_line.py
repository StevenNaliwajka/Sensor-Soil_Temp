#!/usr/bin/env python3
"""
verify_line.py
Checks whether a given input line matches the same pattern
used in parse_line.py and returns True/False accordingly.
"""

import sys
from parse_line import parse_line

def verify_line(line: str) -> bool:
    """Return True if line matches expected pattern, else False."""
    return parse_line(line) is not None

def main():
    # If no args provided, read a single line from stdin
    if len(sys.argv) > 1:
        line = " ".join(sys.argv[1:])
    else:
        line = sys.stdin.readline().strip()

    is_valid = verify_line(line)
    print("True" if is_valid else "False")
    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()
