#!/bin/bash

echo "📧 Generated Email Responses for matthias.buchhorn@web.de"
echo "========================================================="
echo ""

# Get the latest run
RUN_NAME=$(az rest --method GET --uri "https://management.azure.com/subscriptions/6576090b-36b2-4ba1-94ae-d2f52eed2789/resourceGroups/logicapp-jasmin-sweden_group/providers/Microsoft.Logic/workflows/jasmin-email-test-sender/runs?api-version=2016-06-01&\$top=1" --query "value[0].name" -o tsv)

echo "Run ID: $RUN_NAME"
echo ""

# Get all Log_Response actions
RESPONSES=$(az rest --method GET --uri "https://management.azure.com/subscriptions/6576090b-36b2-4ba1-94ae-d2f52eed2789/resourceGroups/logicapp-jasmin-sweden_group/providers/Microsoft.Logic/workflows/jasmin-email-test-sender/runs/$RUN_NAME/actions?api-version=2016-06-01" --query "value[?contains(name,'Log_Response')].properties.outputsLink.uri" -o tsv)

INDEX=1
while IFS= read -r uri; do
    if [ ! -z "$uri" ]; then
        echo "=== EMAIL RESPONSE $INDEX ==="
        
        # Fetch and parse the response
        RESPONSE=$(curl -s "$uri" | jq -r '.[0].inputs')
        
        # Extract email details
        echo "$RESPONSE" | jq -r '"From: \(.originalEmail.from)"'
        echo "$RESPONSE" | jq -r '"Subject: \(.originalEmail.subject)"'
        echo "$RESPONSE" | jq -r '"To: \(.responseEmail.to)"'
        echo "$RESPONSE" | jq -r '"Response Subject: \(.responseEmail.subject)"'
        echo ""
        echo "AI Generated Response:"
        echo "----------------------"
        echo "$RESPONSE" | jq -r '.responseEmail.body' | head -20
        echo "... [truncated for display]"
        echo ""
        echo "============================================="
        echo ""
        
        INDEX=$((INDEX + 1))
    fi
done <<< "$RESPONSES"

echo ""
echo "Note: These responses are prepared but not sent via SMTP yet."
echo "To actually send emails, we need to configure SMTP settings."