#!/usr/bin/env bash
# run.sh — debug-friendly launcher for Codebase/run.py
set -Eeuo pipefail

cd "$(dirname "$0")"

# Logging: pipe all stdout/stderr to run.log
LOG_FILE="$(pwd)/run.log"
touch "$LOG_FILE"
exec 1>>"$LOG_FILE" 2>&1

echo "==== $(date -Iseconds) run.sh starting ===="
echo "PWD: $(pwd)"
echo "User: $(id)"
echo "Groups: $(id -nG)"
echo "PATH: $PATH"
echo "Python: $(command -v python3) — $(python3 -V || true)"
echo "List Codebase/:"
ls -l Codebase || true
echo "--------------------------------------------"

# If you use a venv, uncomment:
# VENV="$(pwd)/.venv"
# if [[ -d "$VENV" ]]; then
#   echo "Activating venv: $VENV"
#   source "$VENV/bin/activate"
# fi

export PYTHONUNBUFFERED=1
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin

# Run and propagate exit code with logging
echo "$(date -Iseconds) launching: python3 Codebase/run.py"
set +e
/usr/bin/python3 Codebase/run.py
RC=$?
set -e
echo "$(date -Iseconds) Codebase/run.py exited with RC=$RC"
echo "==== $(date -Iseconds) run.sh finished ===="
exit $RC
