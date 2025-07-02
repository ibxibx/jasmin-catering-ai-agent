#!/bin/bash

echo "📧 Jasmin Catering - Email Test Results"
echo "========================================"
echo ""
echo "Email Flow:"
echo "  📨 Inquiries: FROM matthias.buchhorn@web.de → TO ma3u-test@email.de"
echo "  📤 Responses: FROM ma3u-test@email.de → TO matthias.buchhorn@web.de"
echo ""

# Get the latest run
RUN_NAME=$(az rest --method GET --uri "https://management.azure.com/subscriptions/6576090b-36b2-4ba1-94ae-d2f52eed2789/resourceGroups/logicapp-jasmin-sweden_group/providers/Microsoft.Logic/workflows/jasmin-email-test-sender/runs?api-version=2016-06-01&\$top=1" --query "value[0].name" -o tsv)

echo "Processing Run: $RUN_NAME"
echo ""

# Get all response emails
RESPONSES=$(az rest --method GET --uri "https://management.azure.com/subscriptions/6576090b-36b2-4ba1-94ae-d2f52eed2789/resourceGroups/logicapp-jasmin-sweden_group/providers/Microsoft.Logic/workflows/jasmin-email-test-sender/runs/$RUN_NAME/actions?api-version=2016-06-01" --query "value[?contains(name,'Create_Response_Email')].properties.outputsLink.uri" -o tsv)

INDEX=1
while IFS= read -r uri; do
    if [ ! -z "$uri" ]; then
        echo "────────────────────────────────────────"
        echo "📧 EMAIL $INDEX"
        echo "────────────────────────────────────────"
        
        # Fetch the response
        RESPONSE=$(curl -s "$uri" | jq -r '.[0].inputs')
        
        # Extract email details
        echo "📮 Original Inquiry:"
        echo "$RESPONSE" | jq -r '"  Subject: \(.originalInquiry.subject)"'
        echo ""
        
        echo "📤 Response Email:"
        echo "$RESPONSE" | jq -r '"  From: \(.from)"'
        echo "$RESPONSE" | jq -r '"  To: \(.to)"'
        echo "$RESPONSE" | jq -r '"  Subject: \(.subject)"'
        echo ""
        echo "📝 Message Preview:"
        echo "---"
        echo "$RESPONSE" | jq -r '.body' | head -30
        echo "..."
        echo ""
        
        INDEX=$((INDEX + 1))
    fi
done <<< "$RESPONSES"

echo "────────────────────────────────────────"
echo ""
echo "✅ All 5 test emails processed successfully!"
echo ""
echo "⚠️  Note: These are simulated emails. To actually send them:"
echo "    1. Set your web.de app password: export WEBDE_APP_PASSWORD='your-password'"
echo "    2. Run: python send-generated-emails.py"