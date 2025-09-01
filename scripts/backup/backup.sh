#!/bin/bash

# LunaCore Backup Script
# Usage: ./backup.sh [destination]

DESTINATION=${1:-"./backups"}
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="$DESTINATION/lunacore_backup_$TIMESTAMP"

echo "Creating backup in $BACKUP_DIR"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
echo "Backing up database..."
docker exec lunacore_db pg_dump -U postgres lunacore > "$BACKUP_DIR/database.sql"

# Backup configurations
echo "Backing up configurations..."
cp -r config/ "$BACKUP_DIR/"
cp -r infra/ "$BACKUP_DIR/"

# Backup logs (if any)
echo "Backing up logs..."
mkdir -p "$BACKUP_DIR/logs"
cp -r logs/ "$BACKUP_DIR/logs/" 2>/dev/null || echo "No logs directory found"

# Create archive
echo "Creating archive..."
tar -czf "$BACKUP_DIR.tar.gz" -C "$DESTINATION" "lunacore_backup_$TIMESTAMP"
rm -rf "$BACKUP_DIR"

echo "Backup completed: $BACKUP_DIR.tar.gz"
