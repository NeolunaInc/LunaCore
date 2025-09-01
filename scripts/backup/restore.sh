#!/bin/bash

# LunaCore Restore Script
# Usage: ./restore.sh <backup_archive>

if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_archive>"
    exit 1
fi

BACKUP_ARCHIVE=$1
RESTORE_DIR="./restore_temp"

echo "Restoring from $BACKUP_ARCHIVE"

# Extract archive
mkdir -p "$RESTORE_DIR"
tar -xzf "$BACKUP_ARCHIVE" -C "$RESTORE_DIR"

# Find the backup directory
BACKUP_DIR=$(find "$RESTORE_DIR" -name "lunacore_backup_*" -type d | head -1)

if [ -z "$BACKUP_DIR" ]; then
    echo "No valid backup directory found in archive"
    exit 1
fi

echo "Restoring from $BACKUP_DIR"

# Restore database
echo "Restoring database..."
docker exec -i lunacore_db psql -U postgres lunacore < "$BACKUP_DIR/database.sql"

# Restore configurations
echo "Restoring configurations..."
cp -r "$BACKUP_DIR/config/"* config/
cp -r "$BACKUP_DIR/infra/"* infra/

# Restore logs
echo "Restoring logs..."
cp -r "$BACKUP_DIR/logs/"* logs/ 2>/dev/null || echo "No logs to restore"

# Cleanup
rm -rf "$RESTORE_DIR"

echo "Restore completed"
