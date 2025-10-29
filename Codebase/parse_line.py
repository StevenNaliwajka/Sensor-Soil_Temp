import re

PATTERN = re.compile(
    r'^Set(\d{1,3}): Soil Moisture: (\d+) \| '
    r'Soil Moisture \(%\): (\d+)% \| '
    r'Soil Temperature:\s*([\d.]+)\s*°C$'
)

def parse_line(line: str):
    m = PATTERN.match(line.strip())
    if not m:
        return None
    set_id = int(m.group(1))
    soil_moisture_raw = int(m.group(2))
    soil_moisture_percent = int(m.group(3))
    soil_temperature_c = float(m.group(4))
    return {
        "set_id": set_id,
        "soil_moisture_raw": soil_moisture_raw,
        "soil_moisture_percent": soil_moisture_percent,
        "soil_temperature_c": soil_temperature_c
    }