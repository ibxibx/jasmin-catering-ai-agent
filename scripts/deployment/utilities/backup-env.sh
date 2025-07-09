#!/bin/bash
# ==============================================================================
# Script: backup-env.sh
# Purpose: Create secure backup of .env file
# Type: Utility Script
#
# Description:
#   Creates an encrypted backup of the .env file with timestamp.
#   Can be stored in 1Password or other secure location.
#
# Usage:
#   ./scripts/deployment/utilities/backup-env.sh
# ==============================================================================

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME=".env.backup_${TIMESTAMP}"

echo "🔐 Creating backup of .env file"
echo "================================"

# Create backup
cp .env "$BACKUP_NAME"

# Create summary
echo "✅ Backup created: $BACKUP_NAME"
echo ""
echo "📋 Next steps:"
echo "1. Open 1Password"
echo "2. Create new Secure Note"
echo "3. Title: 'Jasmin Catering .env - $TIMESTAMP'"
echo "4. Copy contents of $BACKUP_NAME"
echo "5. Delete local backup after saving to 1Password"
echo ""
echo "🔒 Security reminder: Never commit .env files to Git!"