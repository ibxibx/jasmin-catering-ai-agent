#!/bin/bash
# ==============================================================================
# Script: test-azure-deployment.sh
# Purpose: Test the deployed Azure Container Apps Job
# Type: Testing Script
#
# Description:
#   Sends a test email and monitors the Container Apps Job to verify
#   it processes the email correctly with duplicate prevention.
#
# Usage:
#   ./scripts/testing/test-azure-deployment.sh
# ==============================================================================

echo "🧪 Azure Deployment Test"
echo "======================="
echo ""

# Send test email
echo "1️⃣ Sending test email..."
python scripts/testing/send-test-email.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to send test email"
    exit 1
fi

echo ""
echo "2️⃣ Waiting for next job execution (max 5 minutes)..."
echo "   Current time: $(date +%H:%M:%S)"

# Wait for next 5-minute mark
SECONDS_TO_WAIT=$((300 - $(date +%s) % 300 + 30))
echo "   Waiting $SECONDS_TO_WAIT seconds for job to run..."
sleep $SECONDS_TO_WAIT

echo ""
echo "3️⃣ Checking job execution logs..."
./scripts/deployment/monitoring/monitor-container-job.sh latest | tail -20

echo ""
echo "4️⃣ Verifying duplicate prevention..."
# Send another identical email
python scripts/testing/send-test-email.py

# Wait for next execution
echo "   Waiting for second job run..."
sleep 310

echo ""
echo "5️⃣ Checking second execution (should skip duplicate)..."
./scripts/deployment/monitoring/monitor-container-job.sh latest | grep -E "(Already processed|Skipping|UNSEEN)"

echo ""
echo "✅ Azure deployment test complete!"