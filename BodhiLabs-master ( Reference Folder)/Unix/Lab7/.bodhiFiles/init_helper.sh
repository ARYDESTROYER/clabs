#!/bin/bash

# Directory containing files with different MIME types
SOURCE_DIR="/home/.evaluationScripts/.bodhiFiles/files"
TARGET_FILE="/home/labDirectory/mystery_file"
BACKUP_COPY="/tmp/mystery_file_backup"

# Select a random file
RANDOM_FILE=$(ls "$SOURCE_DIR" | shuf -n 1)

# Copy it to the working directory as 'mystery_file'
cp "$SOURCE_DIR/$RANDOM_FILE" "$TARGET_FILE"

# Copy RANDOM_FILE to a backup location
cp "$TARGET_FILE" "$BACKUP_COPY"
