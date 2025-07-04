#!/bin/bash
# Validate Azure AI Foundry setup before deployment

set -e

echo "🔍 Validating Azure AI Foundry Setup"
echo "===================================="

# Check Azure CLI
echo "1. Checking Azure CLI..."
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found"
    exit 1
fi

# Check authentication
if ! az account show &> /dev/null; then
    echo "❌ Not logged into Azure CLI"
    exit 1
fi
echo "✅ Azure CLI authenticated"

# Check subscription
SUBSCRIPTION=$(az account show --query name -o tsv)
echo "✅ Using subscription: $SUBSCRIPTION"

# Check location support for AI services
echo ""
echo "2. Checking AI services availability in Sweden Central..."
OPENAI_AVAILABLE=$(az provider show -n Microsoft.CognitiveServices --query "resourceTypes[?resourceType=='accounts'].locations" -o tsv | grep -i "sweden central" || echo "")

if [ -z "$OPENAI_AVAILABLE" ]; then
    echo "⚠️  Warning: OpenAI might not be available in Sweden Central"
    echo "   Available regions for OpenAI with Assistants API:"
    echo "   - East US"
    echo "   - West Europe"
    echo "   - France Central"
    echo "   - UK South"
    echo ""
    read -p "Continue with Sweden Central anyway? (y/N): " response
    if [[ ! "$response" =~ ^[yY] ]]; then
        exit 1
    fi
else
    echo "✅ AI services available in Sweden Central"
fi

# Check ML workspace provider (for AI Hub)
echo ""
echo "3. Checking Azure ML provider registration..."
ML_STATE=$(az provider show -n Microsoft.MachineLearningServices --query registrationState -o tsv 2>/dev/null || echo "NotRegistered")

if [ "$ML_STATE" != "Registered" ]; then
    echo "⚠️  Azure ML provider not registered. Registering now..."
    az provider register -n Microsoft.MachineLearningServices
    echo "⏳ Waiting for registration (this may take a few minutes)..."
    
    while [ "$ML_STATE" != "Registered" ]; do
        sleep 10
        ML_STATE=$(az provider show -n Microsoft.MachineLearningServices --query registrationState -o tsv)
        echo -n "."
    done
    echo ""
fi
echo "✅ Azure ML provider registered"

# Check environment variables
echo ""
echo "4. Checking environment variables..."
# Load from .env file directly
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  .env file not found, checking environment variables..."
fi

MISSING_VARS=()
[ -z "$WEBDE_APP_PASSWORD" ] && MISSING_VARS+=("WEBDE_APP_PASSWORD")
[ -z "$SLACK_BOT_TOKEN" ] && MISSING_VARS+=("SLACK_BOT_TOKEN")
[ -z "$SLACK_CHANNEL_ID" ] && MISSING_VARS+=("SLACK_CHANNEL_ID")
[ -z "$SLACK_LOG_CHANNEL_ID" ] && MISSING_VARS+=("SLACK_LOG_CHANNEL_ID")

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo "❌ Missing environment variables:"
    printf '   - %s\n' "${MISSING_VARS[@]}"
    echo ""
    echo "Please ensure these are set in your .env file"
    exit 1
fi
echo "✅ All required environment variables found"

# Check Python dependencies
echo ""
echo "5. Checking Python dependencies..."
python -c "import azure.ai.agents" 2>/dev/null && echo "✅ azure-ai-agents installed" || echo "⚠️  azure-ai-agents not installed - run: pip install azure-ai-agents"

# Summary
echo ""
echo "📊 Validation Summary"
echo "===================="
echo "✅ Azure CLI: Ready"
echo "✅ Subscription: $SUBSCRIPTION"
echo "✅ Location: Sweden Central"
echo "✅ ML Provider: Registered"
echo "✅ Environment: Configured"
echo ""
echo "🚀 Ready to deploy AI Foundry!"
echo ""
echo "Next steps:"
echo "1. Run ./deploy-with-ai-foundry.sh to deploy"
echo "2. Run python create-ai-agent-sdk.py to create agent"
echo ""
echo "⚠️  Important: This will create new resources with costs:"
echo "   - Azure OpenAI: ~$50-80/month"
echo "   - Container Apps: ~$2-8/month"
echo "   - Other services: ~$28-32/month"
echo "   Total: ~$80-120/month"