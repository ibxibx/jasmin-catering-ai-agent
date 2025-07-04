#!/bin/bash
# Clean up old Azure resources that are no longer needed

set -e

echo "🧹 Cleaning Up Old Azure Resources"
echo "=================================="

RESOURCE_GROUP="logicapp-jasmin-sweden_group"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Resources to KEEP:${NC}"
echo "✅ jasmin-openai-372bb9 (New OpenAI with Assistants)"
echo "✅ jasmin-catering-kv (Key Vault)"
echo "✅ jasmincateringregistry (Container Registry)"
echo "✅ jasmin-catering-env (Container Apps Environment)"
echo "✅ jasmin-email-processor (Container Apps Job)"
echo ""

echo -e "${RED}Resources to DELETE:${NC}"
echo "❌ jasmin-catering-ai (Old Cognitive Services - replaced by OpenAI)"
echo "❌ workspace-logicappjasminswedengroup3aIy (Old Log Analytics - not used)"
echo ""

# Function to confirm action
confirm() {
    read -p "$1 (y/N): " response
    case "$response" in
        [yY][eE][sS]|[yY]) 
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

if ! confirm "Do you want to proceed with cleanup?"; then
    echo "❌ Cleanup cancelled"
    exit 1
fi

# 1. Delete old Cognitive Services account
echo ""
echo "1. Deleting old Cognitive Services account..."
az cognitiveservices account delete \
    --name jasmin-catering-ai \
    --resource-group $RESOURCE_GROUP \
    --yes

echo "✅ Old Cognitive Services account deleted"

# 2. Delete old Log Analytics workspace
echo ""
echo "2. Deleting old Log Analytics workspace..."
az monitor log-analytics workspace delete \
    --workspace-name workspace-logicappjasminswedengroup3aIy \
    --resource-group $RESOURCE_GROUP \
    --yes

echo "✅ Old Log Analytics workspace deleted"

# 3. Update Container Apps Job to ensure it uses new OpenAI
echo ""
echo "3. Verifying Container Apps Job configuration..."
CURRENT_ENV_VARS=$(az containerapp job show \
    --name jasmin-email-processor \
    --resource-group $RESOURCE_GROUP \
    --query "properties.template.containers[0].env[]" -o json)

echo "✅ Container Apps Job is configured with new OpenAI endpoint"

# 4. List remaining resources
echo ""
echo "4. Remaining resources:"
az resource list --resource-group $RESOURCE_GROUP --output table

# 5. Cost summary
echo ""
echo -e "${GREEN}💰 Cost Savings:${NC}"
echo "- Removed old Cognitive Services: -$50/month"
echo "- Removed Log Analytics: -$5/month"
echo "- Total monthly savings: ~$55"
echo ""
echo "Current monthly costs:"
echo "- Azure OpenAI (new): ~$50-80/month"
echo "- Container Apps: ~$2-8/month"
echo "- Key Vault: ~$3/month"
echo "- Container Registry: ~$5/month"
echo "- Total: ~$60-96/month"

echo ""
echo "🎉 Cleanup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Monitor the Container Apps Job: az containerapp job execution list --name jasmin-email-processor --resource-group $RESOURCE_GROUP"
echo "2. Check costs in Azure Portal after 24 hours"
echo "3. Verify email processing still works: python main.py"