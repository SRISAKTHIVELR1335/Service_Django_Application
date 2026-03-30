#!/usr/bin/env bash
set -e

TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
OUTPUT_DIR=backups
mkdir -p "$OUTPUT_DIR"

echo "[NIRIX] Backing up MySQL database nirix_diagnostics..."
mysqldump -h localhost -u nirix_user -p nirix_diagnostics > "$OUTPUT_DIR/nirix_diagnostics_$TIMESTAMP.sql"

echo "[NIRIX] Backup saved to $OUTPUT_DIR/nirix_diagnostics_$TIMESTAMP.sql"
