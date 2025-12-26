#!/bin/bash
# Simple deployment - just SCP the files without SSH backup logic

if [ $# -lt 1 ]; then
    echo "Usage: $0 <rdf_file> [remote_server]"
    exit 1
fi

LOCAL_FILE="$1"
SERVER="${2:-root@45.56.106.79}"
REMOTE_DIR="/var/ftp/RePEc/bjn/evalua"
FILENAME=$(basename "$LOCAL_FILE")

echo "Deploying: $LOCAL_FILE"
echo "To: $SERVER:$REMOTE_DIR/$FILENAME"
echo ""

if [ ! -f "$LOCAL_FILE" ]; then
    echo "Error: File not found: $LOCAL_FILE"
    exit 1
fi

scp "$LOCAL_FILE" "$SERVER:$REMOTE_DIR/$FILENAME"

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Upload successful!"
else
    echo ""
    echo "✗ Upload failed"
    exit 1
fi
