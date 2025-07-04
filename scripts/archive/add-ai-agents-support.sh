#!/bin/bash
# Add Azure OpenAI with AI Agents support to existing infrastructure

set -e

echo "🤖 Adding AI Agents Support to Jasmin Catering"
echo "=============================================="

# Configuration
RESOURCE_GROUP="logicapp-jasmin-sweden_group"
LOCATION="swedencentral"
KEY_VAULT_NAME="jasmin-catering-kv"

# Generate unique suffix
UNIQUE_SUFFIX=$(echo $RANDOM | md5sum | head -c 6)
OPENAI_NAME="jasmin-openai-$UNIQUE_SUFFIX"

echo "Configuration:"
echo "- Resource Group: $RESOURCE_GROUP"
echo "- Location: $LOCATION"
echo "- OpenAI Resource: $OPENAI_NAME"
echo ""

# 1. Create Azure OpenAI resource with Assistants support
echo "1. Creating Azure OpenAI resource..."
az cognitiveservices account create \
    --name $OPENAI_NAME \
    --resource-group $RESOURCE_GROUP \
    --kind OpenAI \
    --sku S0 \
    --location $LOCATION \
    --custom-domain $OPENAI_NAME \
    --yes

echo "✅ OpenAI resource created: $OPENAI_NAME"

# 2. Deploy GPT-4o model
echo "2. Deploying GPT-4o model..."
# Wait for resource to be ready
sleep 30

az cognitiveservices account deployment create \
    --name $OPENAI_NAME \
    --resource-group $RESOURCE_GROUP \
    --deployment-name gpt-4o \
    --model-name gpt-4o \
    --model-version "2024-08-06" \
    --model-format OpenAI \
    --sku-name "Standard" \
    --sku-capacity 10

echo "✅ GPT-4o model deployed"

# 3. Get OpenAI endpoint and key
echo "3. Retrieving OpenAI credentials..."
OPENAI_ENDPOINT=$(az cognitiveservices account show \
    --name $OPENAI_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.endpoint -o tsv)

OPENAI_KEY=$(az cognitiveservices account keys list \
    --name $OPENAI_NAME \
    --resource-group $RESOURCE_GROUP \
    --query key1 -o tsv)

echo "✅ OpenAI endpoint: $OPENAI_ENDPOINT"

# 4. Update Key Vault
echo "4. Updating Key Vault secrets..."
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "openai-endpoint" --value "$OPENAI_ENDPOINT" --output none
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "openai-api-key" --value "$OPENAI_KEY" --output none

echo "✅ Secrets updated in Key Vault"

# 5. Update .env file
echo "5. Updating .env file..."

# Backup existing .env
if [ -f ".env" ]; then
    cp .env .env.backup
    echo "✅ Backed up existing .env to .env.backup"
fi

# Add new OpenAI configuration
if [ -f ".env" ]; then
    # Remove old AI configuration if exists
    grep -v "AZURE_AI_API_KEY\|AZURE_AI_ENDPOINT\|AZURE_OPENAI" .env > .env.tmp || true
    mv .env.tmp .env
fi

# Append new configuration
cat >> .env << EOF

# Azure OpenAI Configuration (with AI Agents support)
AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT
AZURE_OPENAI_API_KEY=$OPENAI_KEY
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_RESOURCE_NAME=$OPENAI_NAME
EOF

echo "✅ .env file updated"

# 6. Update existing Container Apps Job with new environment variables
echo "6. Updating Container Apps Job..."
JOB_NAME="jasmin-email-processor"

# Get existing environment variables
EXISTING_ENV_VARS=$(az containerapp job show \
    --name $JOB_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "properties.configuration.triggerConfig.scheduleTriggerConfig" -o json)

# Update with new OpenAI configuration
az containerapp job update \
    --name $JOB_NAME \
    --resource-group $RESOURCE_GROUP \
    --set environmentVariables[?name=='AZURE_OPENAI_ENDPOINT'].value="$OPENAI_ENDPOINT" \
    --set environmentVariables[?name=='AZURE_OPENAI_API_KEY'].value="$OPENAI_KEY" \
    --set environmentVariables[?name=='AZURE_AI_ENDPOINT'].value="$OPENAI_ENDPOINT" \
    --set environmentVariables[?name=='AZURE_AI_API_KEY'].value="$OPENAI_KEY"

echo "✅ Container Apps Job updated"

echo ""
echo "🎉 AI Agents Support Added Successfully!"
echo "========================================"
echo "✅ OpenAI Resource: $OPENAI_NAME"
echo "✅ Endpoint: $OPENAI_ENDPOINT"
echo "✅ Model: gpt-4o (with Assistants API)"
echo "✅ Key Vault: Updated"
echo "✅ Container App: Updated"
echo ""
echo "📊 Next Steps:"
echo "1. Run: python create-ai-agent-sdk.py"
echo "   This will create an AI Agent with knowledge store"
echo ""
echo "2. Test locally:"
echo "   python main.py"
echo ""
echo "3. Deploy and test in cloud:"
echo "   az containerapp job start --name $JOB_NAME --resource-group $RESOURCE_GROUP"
echo ""
echo "💰 Additional Monthly Cost: ~$50-80 for Azure OpenAI"