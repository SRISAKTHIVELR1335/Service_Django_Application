#!/usr/bin/env bash
set -e

if [ -z "$1" ]; then
  echo "Usage: restore_mysql.sh <backup-file.sql>"
  exit 1
fi

BACKUP_FILE="$1"

echo "[NIRIX] Restoring MySQL database nirix_diagnostics from $BACKUP_FILE..."
mysql -h localhost -u nirix_user -p nirix_diagnostics < "$BACKUP_FILE"

echo "[NIRIX] Restore completed."
