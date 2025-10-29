#!/bin/bash
# setup_autostart.sh
# Configures systemd to run run.sh on boot

SERVICE_NAME="custom-startup"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUN_SCRIPT="$SCRIPT_DIR/run.sh"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# Check for root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (e.g. sudo bash $0)"
  exit 1
fi

# Check if run.sh exists
if [ ! -f "$RUN_SCRIPT" ]; then
  echo "Error: run.sh not found in $SCRIPT_DIR"
  exit 1
fi

# Create systemd service file
cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Run custom script at startup
After=network.target

[Service]
Type=simple
WorkingDirectory=$SCRIPT_DIR
ExecStart=/bin/bash $RUN_SCRIPT
Restart=always
User=$(logname)

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd, enable and start service
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"

echo "✅ Service '$SERVICE_NAME' created and started."
echo "→ It will automatically run $RUN_SCRIPT on boot."
