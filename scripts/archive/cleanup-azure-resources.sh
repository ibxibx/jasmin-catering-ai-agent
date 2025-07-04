#!/bin/bash
# Cleanup Azure Resources for Jasmin Catering
# This removes unused services and keeps only what's needed

echo "🧹 Jasmin Catering - Azure Resource Cleanup"
echo "==========================================="

# 1. Disable Logic App (stop the 5-minute timer)
echo "1. Disabling Logic App..."
az logic workflow update \
  --resource-group logicapp-jasmin-sweden_group \
  --name jasmin-order-processor-sweden \
  --state Disabled

echo "✅ Logic App disabled"

# 2. Check if we can remove OpenAI service
echo "2. Checking OpenAI service usage..."
echo "⚠️  OpenAI service is still used by Python system - keeping it"

# 3. Remove AI Search service (not used by Python system, expensive)
echo "3. Removing Azure AI Search service..."
read -p "Remove Azure AI Search service? This will delete the jasmin-catering-search service and save ~$250/month. (y/N): " confirm

if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
    az search service delete \
      --resource-group logicapp-jasmin-sweden_group \
      --name jasmin-catering-search \
      --yes
    echo "✅ Azure AI Search service removed"
else
    echo "⏭️  Keeping Azure AI Search service"
fi

# 4. Remove test Logic App
echo "4. Removing test Logic App..."
az logic workflow delete \
  --resource-group logicapp-jasmin-sweden_group \
  --name jasmin-email-test-sender \
  --yes

echo "✅ Test Logic App removed"

# 5. Summary
echo ""
echo "🎉 Cleanup Complete!"
echo "==================="
echo "✅ Logic App disabled (not deleted, can be re-enabled)"
echo "✅ Test Logic App removed"
echo "⚠️  OpenAI service kept (used by Python system)"
echo "📊 Estimated monthly savings: ~$260"
echo ""
echo "Remaining resources:"
echo "- jasmin-catering-kv (Key Vault) - needed"
echo "- jasmin-catering-ai (OpenAI) - needed by Python"
echo "- jasmin-order-processor-sweden (Logic App) - disabled"
echo ""
echo "🐍 Python system (main.py) handles all processing now!"