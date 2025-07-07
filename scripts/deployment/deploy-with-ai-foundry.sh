#!/bin/bash
# Deploy Jasmin Catering with Azure AI Foundry and AI Agents

set -e

echo "🚀 Deploying Jasmin Catering with Azure AI Foundry"
echo "=================================================="

# Load environment variables
source ../../deployments/scripts/load-env-config.sh

# Configuration
RESOURCE_GROUP="logicapp-jasmin-sweden_group"
LOCATION="swedencentral"
AI_HUB_NAME="jasmin-ai-hub"
AI_PROJECT_NAME="jasmin-catering"
AI_MODEL_NAME="gpt-4o"
CONTAINER_APP_ENV="jasmin-catering-env"
JOB_NAME="jasmin-email-processor"
ACR_NAME="jasmincateringregistry"
IMAGE_NAME="jasmin-catering-ai"
KEY_VAULT_NAME="jasmin-catering-kv"

# Generate unique suffix for globally unique names
UNIQUE_SUFFIX=$(echo $RANDOM | md5sum | head -c 6)

echo "Configuration:"
echo "- Resource Group: $RESOURCE_GROUP"
echo "- Location: $LOCATION"
echo "- AI Hub: $AI_HUB_NAME"
echo "- AI Project: $AI_PROJECT_NAME"
echo ""

# 1. Create AI Hub (Azure AI Foundry)
echo "1. Creating Azure AI Hub..."
AI_HUB_ID=$(az ml workspace create \
    --name $AI_HUB_NAME \
    --resource-group $RESOURCE_GROUP \
    --kind hub \
    --location $LOCATION \
    --query id -o tsv)

echo "✅ AI Hub created: $AI_HUB_NAME"

# 2. Create AI Project
echo "2. Creating AI Project..."
AI_PROJECT_ID=$(az ml workspace create \
    --name $AI_PROJECT_NAME \
    --resource-group $RESOURCE_GROUP \
    --kind project \
    --hub-id $AI_HUB_ID \
    --location $LOCATION \
    --query id -o tsv)

echo "✅ AI Project created: $AI_PROJECT_NAME"

# 3. Create Azure OpenAI resource with Agents support
echo "3. Creating Azure OpenAI resource..."
OPENAI_NAME="jasmin-openai-$UNIQUE_SUFFIX"
az cognitiveservices account create \
    --name $OPENAI_NAME \
    --resource-group $RESOURCE_GROUP \
    --kind OpenAI \
    --sku S0 \
    --location $LOCATION \
    --yes

echo "✅ OpenAI resource created: $OPENAI_NAME"

# 4. Deploy GPT-4o model
echo "4. Deploying GPT-4o model..."
az cognitiveservices account deployment create \
    --name $OPENAI_NAME \
    --resource-group $RESOURCE_GROUP \
    --deployment-name $AI_MODEL_NAME \
    --model-name gpt-4o \
    --model-version "2024-08-06" \
    --model-format OpenAI \
    --sku-name "Standard" \
    --sku-capacity 10

echo "✅ GPT-4o model deployed"

# 5. Get OpenAI endpoint and key
echo "5. Retrieving OpenAI credentials..."
OPENAI_ENDPOINT=$(az cognitiveservices account show \
    --name $OPENAI_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.endpoint -o tsv)

OPENAI_KEY=$(az cognitiveservices account keys list \
    --name $OPENAI_NAME \
    --resource-group $RESOURCE_GROUP \
    --query key1 -o tsv)

echo "✅ OpenAI endpoint: $OPENAI_ENDPOINT"

# 6. Create Key Vault
echo "6. Creating Key Vault..."
az keyvault create \
    --name $KEY_VAULT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --enable-rbac-authorization false

echo "✅ Key Vault created: $KEY_VAULT_NAME"

# 7. Store secrets in Key Vault
echo "7. Storing secrets in Key Vault..."
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "openai-endpoint" --value "$OPENAI_ENDPOINT"
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "openai-api-key" --value "$OPENAI_KEY"
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "webde-app-password" --value "$WEBDE_APP_PASSWORD"
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "slack-bot-token" --value "$SLACK_BOT_TOKEN"
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "slack-channel-emailrequestsandresponse" --value "$SLACK_CHANNEL_ID"
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "slack-channel-jasminlogs" --value "$SLACK_LOG_CHANNEL_ID"

echo "✅ Secrets stored in Key Vault"

# 8. Update .env file
echo "8. Updating .env file..."
cat > .env << EOF
# Azure Configuration
AZURE_SUBSCRIPTION_ID=$AZURE_SUBSCRIPTION_ID
AZURE_RESOURCE_GROUP=$RESOURCE_GROUP
AZURE_LOCATION=$LOCATION
AZURE_KEY_VAULT_NAME=$KEY_VAULT_NAME

# Azure OpenAI Configuration (with Agents support)
AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT
AZURE_OPENAI_API_KEY=$OPENAI_KEY
AZURE_OPENAI_DEPLOYMENT_NAME=$AI_MODEL_NAME

# AI Project Configuration
AZURE_AI_HUB_NAME=$AI_HUB_NAME
AZURE_AI_PROJECT_NAME=$AI_PROJECT_NAME
AZURE_AI_PROJECT_ID=$AI_PROJECT_ID

# Email Configuration
FROM_EMAIL_ADDRESS=matthias.buchhorn@web.de
WEBDE_APP_PASSWORD=$WEBDE_APP_PASSWORD
WEBDE_EMAIL_ALIAS=ma3u-test@email.de

# Slack Configuration
SLACK_BOT_TOKEN=$SLACK_BOT_TOKEN
SLACK_CHANNEL_ID=$SLACK_CHANNEL_ID
SLACK_LOG_CHANNEL_ID=$SLACK_LOG_CHANNEL_ID
EOF

echo "✅ .env file updated"

# 9. Create Container Registry
echo "9. Creating Container Registry..."
az acr create \
    --name $ACR_NAME \
    --resource-group $RESOURCE_GROUP \
    --sku Basic \
    --admin-enabled true

echo "✅ Container Registry created: $ACR_NAME"

# 10. Create Container Apps Environment
echo "10. Creating Container Apps Environment..."
az containerapp env create \
    --name $CONTAINER_APP_ENV \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

echo "✅ Container Apps Environment created"

# 11. Build and push Docker image
echo "11. Building and pushing Docker image..."
az acr build \
    --registry $ACR_NAME \
    --image $IMAGE_NAME:latest \
    --file Dockerfile .

echo "✅ Docker image built and pushed"

# 12. Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

# 13. Create Container Apps Job
echo "12. Creating Container Apps Job..."
az containerapp job create \
    --name $JOB_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINER_APP_ENV \
    --trigger-type "Schedule" \
    --replica-timeout 300 \
    --replica-retry-limit 2 \
    --replica-completion-count 1 \
    --parallelism 1 \
    --image "$ACR_NAME.azurecr.io/$IMAGE_NAME:latest" \
    --registry-server "$ACR_NAME.azurecr.io" \
    --registry-username "$ACR_USERNAME" \
    --registry-password "$ACR_PASSWORD" \
    --cpu 0.25 \
    --memory 0.5Gi \
    --cron-expression "*/5 * * * *" \
    --env-vars \
        AZURE_OPENAI_ENDPOINT="$OPENAI_ENDPOINT" \
        AZURE_OPENAI_API_KEY="$OPENAI_KEY" \
        AZURE_OPENAI_DEPLOYMENT_NAME="$AI_MODEL_NAME" \
        FROM_EMAIL_ADDRESS="matthias.buchhorn@web.de" \
        WEBDE_APP_PASSWORD="$WEBDE_APP_PASSWORD" \
        WEBDE_EMAIL_ALIAS="ma3u-test@email.de" \
        SLACK_BOT_TOKEN="$SLACK_BOT_TOKEN" \
        SLACK_CHANNEL_ID="$SLACK_CHANNEL_ID" \
        SLACK_LOG_CHANNEL_ID="$SLACK_LOG_CHANNEL_ID" \
        AZURE_RESOURCE_GROUP="$RESOURCE_GROUP" \
        AZURE_KEY_VAULT_NAME="$KEY_VAULT_NAME" \
        AZURE_CONTAINER_APPS="true"

echo "✅ Container Apps Job created"

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo "✅ AI Hub: $AI_HUB_NAME"
echo "✅ AI Project: $AI_PROJECT_NAME"
echo "✅ OpenAI Resource: $OPENAI_NAME (with Agents support)"
echo "✅ Container Apps Job: $JOB_NAME"
echo "✅ Key Vault: $KEY_VAULT_NAME"
echo ""
echo "📊 Next Steps:"
echo "1. Run ./create-ai-agent-sdk.py to create AI Agent"
echo "2. Test with: az containerapp job start --name $JOB_NAME --resource-group $RESOURCE_GROUP"
echo ""
echo "💰 Estimated Monthly Cost: ~$80-120"
echo "   - Azure OpenAI: $50-80"
echo "   - Container Apps: $2-8"
echo "   - Other services: $28-32"