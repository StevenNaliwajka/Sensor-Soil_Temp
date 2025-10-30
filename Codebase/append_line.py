#!/usr/bin/env python3
# Codebase/append_line.py
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Optional

# Project root is parent of "Codebase"
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_OUTPUT_ROOT = _PROJECT_ROOT / "Output"

# CSV header (stable, “universal” names)
_CSV_HEADER = ["timestamp_iso", "set", "soil_moist", "soil_moist_perc", "soil_temp"]


def _ensure_output_paths_for_today(set_num: int, when: Optional[datetime] = None) -> Path:
    """
    Ensure today's folder exists and return the CSV path for the given set.
    Folder format: Output/YYYY-MM-DD
    File format:   YYYY-MM-DD_set<SetNum>.csv
    """
    when = when or datetime.now()  # local time; timestamp column stores full ISO 8601
    day_str = when.date().isoformat()  # 'YYYY-MM-DD'
    day_dir = _OUTPUT_ROOT / day_str
    day_dir.mkdir(parents=True, exist_ok=True)

    csv_path = day_dir / f"{day_str}_set{set_num}.csv"
    if not csv_path.exists():
        # create file with header
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(_CSV_HEADER)
    return csv_path


def append_line(set_num: int, s_moist: float, s_moist_perc: float, s_temp: float) -> None:
    """
    Append one reading to today's CSV for this set, creating folder/file if needed.
    Also prints a concise log to stdout.
    """
    now = datetime.now()
    csv_path = _ensure_output_paths_for_today(set_num, now)

    row = [
        now.isoformat(timespec="seconds"),  # e.g., '2025-10-30T12:45:07'
        set_num,
        s_moist,
        s_moist_perc,
        s_temp,
    ]
    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)

    # Keep your original print format (plus file hint)
    print(
        f"[append_line] Set={set_num}  "
        f"SMoist={s_moist}  "
        f"SMoistPerc={s_moist_perc}  "
        f"STemp={s_temp}  "
        f"-> {csv_path.relative_to(_PROJECT_ROOT)}"
    )


# Optional: quick manual test when run directly.
if __name__ == "__main__":
    # Example: python Codebase/append_line.py
    append_line(set_num=1, s_moist=25.25, s_moist_perc=23.23, s_temp=23.2)
