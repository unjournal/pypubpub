#!/bin/bash
# Deploy RePEc RDF file to Linode server with proper versioning

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 <rdf_file> [remote_server]"
    echo "Example: $0 repec_rdfs/eval2025_04.rdf root@45.56.106.79"
    exit 1
fi

LOCAL_FILE="$1"
SERVER="${2:-root@45.56.106.79}"
REMOTE_DIR="/var/ftp/RePEc/bjn/evalua"
BACKUP_DIR="/var/ftp/RePEc/bjn/evalua/archive"

# Extract filename
FILENAME=$(basename "$LOCAL_FILE")

echo "=========================================="
echo "RePEc RDF Deployment"
echo "=========================================="
echo "Local file: $LOCAL_FILE"
echo "Server: $SERVER"
echo "Remote file: $REMOTE_DIR/$FILENAME"
echo ""

# Check if local file exists
if [ ! -f "$LOCAL_FILE" ]; then
    echo "Error: Local file not found: $LOCAL_FILE"
    exit 1
fi

# Create backup directory on server if it doesn't exist
echo "1. Creating backup directory..."
ssh "$SERVER" "mkdir -p $BACKUP_DIR"

# Backup existing file if it exists
echo "2. Backing up existing file (if present)..."
ssh "$SERVER" "
    if [ -f $REMOTE_DIR/$FILENAME ]; then
        TIMESTAMP=\$(date +%Y%m%d_%H%M%S)
        cp $REMOTE_DIR/$FILENAME $BACKUP_DIR/${FILENAME%.rdf}_\${TIMESTAMP}.rdf
        echo '   Backed up to: $BACKUP_DIR/${FILENAME%.rdf}_\${TIMESTAMP}.rdf'
    else
        echo '   No existing file to backup'
    fi
"

# Upload new file
echo "3. Uploading new file..."
scp "$LOCAL_FILE" "$SERVER:$REMOTE_DIR/$FILENAME"

# Verify upload
echo "4. Verifying upload..."
REMOTE_SIZE=$(ssh "$SERVER" "wc -c < $REMOTE_DIR/$FILENAME")
LOCAL_SIZE=$(wc -c < "$LOCAL_FILE")

if [ "$REMOTE_SIZE" = "$LOCAL_SIZE" ]; then
    echo "   ✓ Upload successful ($REMOTE_SIZE bytes)"
else
    echo "   ✗ Size mismatch! Local: $LOCAL_SIZE, Remote: $REMOTE_SIZE"
    exit 1
fi

# Show recent backups
echo ""
echo "Recent backups:"
ssh "$SERVER" "ls -lht $BACKUP_DIR | head -5"

echo ""
echo "=========================================="
echo "✓ Deployment complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. RePEc will crawl this file (usually within 1-2 weeks)"
echo "2. Records will appear on IDEAS: https://ideas.repec.org/s/bjn/evalua.html"
echo "3. Google Scholar will index from IDEAS (2-4 weeks after that)"

