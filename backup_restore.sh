#!/bin/bash

# AFSP Backup and Restore Script
# This script creates backups of the AFSP application data and provides restore functionality

BACKUP_DIR="/workspaces/Backlogged-Books/backups"
DB_FILE="/workspaces/Backlogged-Books/afsp_app/afsp.db"
UPLOADS_DIR="/workspaces/Backlogged-Books/afsp_app/uploads"
DOWNLOADS_DIR="/workspaces/Backlogged-Books/afsp_app/downloads"
FRONTEND_BUILD_DIR="/workspaces/Backlogged-Books/frontend/build"
DATE_FORMAT=$(date +"%Y%m%d-%H%M%S")

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Show usage information
show_usage() {
  echo "Usage: $0 [backup|restore] [options]"
  echo ""
  echo "Commands:"
  echo "  backup              Create a backup of the application"
  echo "  restore [filename]  Restore from a backup file"
  echo ""
  echo "Options for backup:"
  echo "  --full              Backup database, user files, and frontend build (default)"
  echo "  --db-only           Backup only the database"
  echo "  --files-only        Backup only user files (uploads and downloads)"
  echo ""
  echo "Examples:"
  echo "  $0 backup           # Create a full backup"
  echo "  $0 backup --db-only # Create a database-only backup"
  echo "  $0 restore afsp_backup_20250801-120000.tar.gz # Restore from specific backup"
}

# Create a backup
create_backup() {
  echo "Creating backup..."
  BACKUP_TYPE="full"
  BACKUP_FILE="$BACKUP_DIR/afsp_backup_${DATE_FORMAT}.tar.gz"
  
  # Process options
  if [ "$1" == "--db-only" ]; then
    BACKUP_TYPE="db"
    BACKUP_FILE="$BACKUP_DIR/afsp_db_backup_${DATE_FORMAT}.tar.gz"
  elif [ "$1" == "--files-only" ]; then
    BACKUP_TYPE="files"
    BACKUP_FILE="$BACKUP_DIR/afsp_files_backup_${DATE_FORMAT}.tar.gz"
  fi
  
  # Create temporary directory for the backup
  TEMP_DIR=$(mktemp -d)
  
  # Copy files based on backup type
  if [[ "$BACKUP_TYPE" == "full" || "$BACKUP_TYPE" == "db" ]]; then
    echo "Backing up database..."
    if [ -f "$DB_FILE" ]; then
      # Create a database dump if SQLite is available
      sqlite3 "$DB_FILE" .dump > "$TEMP_DIR/afsp_db_dump.sql"
      cp "$DB_FILE" "$TEMP_DIR/afsp.db"
    else
      echo "Warning: Database file not found at $DB_FILE"
    fi
  fi
  
  if [[ "$BACKUP_TYPE" == "full" || "$BACKUP_TYPE" == "files" ]]; then
    echo "Backing up user files..."
    # Create directories in the temp folder
    mkdir -p "$TEMP_DIR/uploads"
    mkdir -p "$TEMP_DIR/downloads"
    
    # Copy files if directories exist
    if [ -d "$UPLOADS_DIR" ]; then
      cp -R "$UPLOADS_DIR/"* "$TEMP_DIR/uploads/" 2>/dev/null || true
    fi
    
    if [ -d "$DOWNLOADS_DIR" ]; then
      cp -R "$DOWNLOADS_DIR/"* "$TEMP_DIR/downloads/" 2>/dev/null || true
    fi
  fi
  
  if [[ "$BACKUP_TYPE" == "full" ]]; then
    echo "Backing up frontend build..."
    if [ -d "$FRONTEND_BUILD_DIR" ]; then
      mkdir -p "$TEMP_DIR/frontend_build"
      cp -R "$FRONTEND_BUILD_DIR/"* "$TEMP_DIR/frontend_build/" 2>/dev/null || true
    else
      echo "Warning: Frontend build directory not found at $FRONTEND_BUILD_DIR"
    fi
  fi
  
  # Create metadata file
  echo "AFSP Backup" > "$TEMP_DIR/backup_metadata.txt"
  echo "Type: $BACKUP_TYPE" >> "$TEMP_DIR/backup_metadata.txt"
  echo "Date: $(date)" >> "$TEMP_DIR/backup_metadata.txt"
  echo "Version: 1.0.0" >> "$TEMP_DIR/backup_metadata.txt"
  
  # Create the archive
  tar -czf "$BACKUP_FILE" -C "$TEMP_DIR" .
  
  # Clean up
  rm -rf "$TEMP_DIR"
  
  echo "Backup created at $BACKUP_FILE"
  echo "Backup size: $(du -h "$BACKUP_FILE" | cut -f1)"
}

# Restore from a backup
restore_backup() {
  if [ -z "$1" ]; then
    echo "Error: Backup file not specified for restore"
    show_usage
    exit 1
  fi
  
  BACKUP_FILE="$1"
  
  # If not a full path, assume it's in the backup directory
  if [[ ! "$BACKUP_FILE" == /* ]]; then
    BACKUP_FILE="$BACKUP_DIR/$BACKUP_FILE"
  fi
  
  if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
  fi
  
  echo "Restoring from backup: $BACKUP_FILE"
  
  # Create temporary directory for extraction
  TEMP_DIR=$(mktemp -d)
  
  # Extract the archive
  tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"
  
  # Check backup metadata
  if [ -f "$TEMP_DIR/backup_metadata.txt" ]; then
    BACKUP_TYPE=$(grep "Type:" "$TEMP_DIR/backup_metadata.txt" | cut -d' ' -f2)
    echo "Backup type: $BACKUP_TYPE"
  else
    echo "Warning: No metadata found in backup, assuming full backup"
    BACKUP_TYPE="full"
  fi
  
  # Restore database
  if [[ "$BACKUP_TYPE" == "full" || "$BACKUP_TYPE" == "db" ]]; then
    if [ -f "$TEMP_DIR/afsp.db" ]; then
      echo "Restoring database..."
      cp "$TEMP_DIR/afsp.db" "$DB_FILE"
    else
      echo "Warning: Database file not found in backup"
    fi
  fi
  
  # Restore user files
  if [[ "$BACKUP_TYPE" == "full" || "$BACKUP_TYPE" == "files" ]]; then
    echo "Restoring user files..."
    
    # Create directories if they don't exist
    mkdir -p "$UPLOADS_DIR"
    mkdir -p "$DOWNLOADS_DIR"
    
    # Restore files if they exist in the backup
    if [ -d "$TEMP_DIR/uploads" ] && [ "$(ls -A "$TEMP_DIR/uploads" 2>/dev/null)" ]; then
      cp -R "$TEMP_DIR/uploads/"* "$UPLOADS_DIR/"
    fi
    
    if [ -d "$TEMP_DIR/downloads" ] && [ "$(ls -A "$TEMP_DIR/downloads" 2>/dev/null)" ]; then
      cp -R "$TEMP_DIR/downloads/"* "$DOWNLOADS_DIR/"
    fi
  fi
  
  # Restore frontend build
  if [[ "$BACKUP_TYPE" == "full" ]] && [ -d "$TEMP_DIR/frontend_build" ]; then
    echo "Restoring frontend build..."
    mkdir -p "$FRONTEND_BUILD_DIR"
    cp -R "$TEMP_DIR/frontend_build/"* "$FRONTEND_BUILD_DIR/" 2>/dev/null || true
  fi
  
  # Clean up
  rm -rf "$TEMP_DIR"
  
  echo "Restore completed successfully!"
}

# List available backups
list_backups() {
  echo "Available backups:"
  echo "-----------------"
  
  if [ -d "$BACKUP_DIR" ] && [ "$(ls -A "$BACKUP_DIR" 2>/dev/null)" ]; then
    ls -lh "$BACKUP_DIR" | grep -v '^total' | awk '{print $9 " (" $5 ")"}'
  else
    echo "No backups found."
  fi
}

# Main script execution
if [ "$1" == "backup" ]; then
  create_backup "$2"
elif [ "$1" == "restore" ]; then
  restore_backup "$2"
elif [ "$1" == "list" ]; then
  list_backups
else
  show_usage
fi
