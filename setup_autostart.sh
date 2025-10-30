#!/usr/bin/env bash
# setup_autostart.sh — create and enable a systemd service for run.sh

SERVICE_NAME="moisture-temp-monitor"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUN_SCRIPT="$PROJECT_DIR/run.sh"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
USER_NAME=$(logname)

# --- Safety checks ---
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (e.g. sudo bash $0)"
  exit 1
fi

if [ ! -f "$RUN_SCRIPT" ]; then
  echo "Error: run.sh not found at $RUN_SCRIPT"
  exit 1
fi

# --- Create service file ---
cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Run custom Sensor-Soil_Temp script at startup
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER_NAME
Group=$USER_NAME
WorkingDirectory=$PROJECT_DIR
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin
Environment=PYTHONUNBUFFERED=1
ExecStart=/usr/bin/env bash $RUN_SCRIPT
Restart=on-failure
RestartSec=5
StandardOutput=append:$PROJECT_DIR/run.log
StandardError=append:$PROJECT_DIR/run.log

[Install]
WantedBy=multi-user.target
EOF

# --- Enable + start the service ---
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

echo "Service '$SERVICE_NAME' installed and started."
echo "→ Logs will be stored in: $PROJECT_DIR/run.log"
echo "→ Check status: sudo systemctl status $SERVICE_NAME"
