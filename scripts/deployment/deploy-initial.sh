#!/bin/bash
# Initial deployment script for Jasmin Catering AI Agent

set -e

echo "🚀 Initial Deployment: Jasmin Catering AI Agent"
echo "=============================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found. Please create it with required secrets."
    exit 1
fi

# Load environment variables
source .env

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
UNIQUE_SUFFIX=$(openssl rand -hex 3)

echo "Configuration:"
echo "- Resource Group: $RESOURCE_GROUP"
echo "- Location: $LOCATION"
echo "- Unique Suffix: $UNIQUE_SUFFIX"
echo ""

# Check if Azure CLI is logged in
echo "1. Checking Azure CLI authentication..."
if ! az account show &> /dev/null; then
    echo "❌ Not logged into Azure CLI. Please run 'az login' first."
    exit 1
fi
echo "✅ Azure CLI authenticated"

# Set subscription
echo "2. Setting Azure subscription..."
az account set --subscription $AZURE_SUBSCRIPTION_ID
echo "✅ Subscription set: $AZURE_SUBSCRIPTION_ID"

# Create resource group if it doesn't exist
echo "3. Creating resource group..."
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION
echo "✅ Resource group ready: $RESOURCE_GROUP"

# Create Azure OpenAI resource
echo "4. Creating Azure OpenAI resource..."
OPENAI_NAME="jasmin-openai-$UNIQUE_SUFFIX"
az cognitiveservices account create \
    --name $OPENAI_NAME \
    --resource-group $RESOURCE_GROUP \
    --kind OpenAI \
    --sku S0 \
    --location $LOCATION \
    --yes

echo "✅ OpenAI resource created: $OPENAI_NAME"

# Deploy GPT-4o model
echo "5. Deploying GPT-4o model..."
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

# Get OpenAI endpoint and key
echo "6. Retrieving OpenAI credentials..."
OPENAI_ENDPOINT=$(az cognitiveservices account show \
    --name $OPENAI_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.endpoint -o tsv)

OPENAI_KEY=$(az cognitiveservices account keys list \
    --name $OPENAI_NAME \
    --resource-group $RESOURCE_GROUP \
    --query key1 -o tsv)

echo "✅ OpenAI credentials retrieved"

# Create Key Vault
echo "7. Creating Key Vault..."
az keyvault create \
    --name $KEY_VAULT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --enable-rbac-authorization false

echo "✅ Key Vault created: $KEY_VAULT_NAME"

# Store secrets in Key Vault
echo "8. Storing secrets in Key Vault..."
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "openai-endpoint" --value "$OPENAI_ENDPOINT"
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "openai-api-key" --value "$OPENAI_KEY"
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "azure-ai-api-key" --value "$OPENAI_KEY"
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "webde-app-password" --value "$WEBDE_APP_PASSWORD"
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "slack-bot-token" --value "$SLACK_BOT_TOKEN"
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "slack-channel-emailrequestsandresponse" --value "$SLACK_CHANNEL_ID"
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "slack-channel-jasminlogs" --value "$SLACK_LOG_CHANNEL_ID"

echo "✅ Secrets stored in Key Vault"

# Update .env file
echo "9. Updating .env file..."
sed -i "s|AZURE_OPENAI_ENDPOINT=.*|AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT|g" .env
sed -i "s|AZURE_OPENAI_API_KEY=.*|AZURE_OPENAI_API_KEY=$OPENAI_KEY|g" .env
sed -i "s|AZURE_KEY_VAULT_NAME=.*|AZURE_KEY_VAULT_NAME=$KEY_VAULT_NAME|g" .env

echo "✅ .env file updated"

# Create Container Registry
echo "10. Creating Container Registry..."
az acr create \
    --name $ACR_NAME \
    --resource-group $RESOURCE_GROUP \
    --sku Basic \
    --admin-enabled true

echo "✅ Container Registry created: $ACR_NAME"

# Create Container Apps Environment
echo "11. Creating Container Apps Environment..."
az containerapp env create \
    --name $CONTAINER_APP_ENV \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

echo "✅ Container Apps Environment created"

# Build and push Docker image
echo "12. Building and pushing Docker image..."
az acr build \
    --registry $ACR_NAME \
    --image $IMAGE_NAME:latest \
    --file Dockerfile .

echo "✅ Docker image built and pushed"

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

# Create Container Apps Job
echo "13. Creating Container Apps Job..."
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
echo "🎉 Initial Deployment Complete!"
echo "==============================="
echo "✅ OpenAI Resource: $OPENAI_NAME"
echo "✅ Key Vault: $KEY_VAULT_NAME"
echo "✅ Container Registry: $ACR_NAME"
echo "✅ Container Apps Job: $JOB_NAME"
echo "✅ Schedule: Every 5 minutes (*/5 * * * *)"
echo ""
echo "📊 Next Steps:"
echo "1. Test the deployment: az containerapp job start --name $JOB_NAME --resource-group $RESOURCE_GROUP"
echo "2. Monitor logs: az containerapp job logs show --name $JOB_NAME --resource-group $RESOURCE_GROUP"
echo "3. Check Slack channels for notifications"
echo ""
echo "💰 Estimated Monthly Cost: ~$60-96"
echo "   - Azure OpenAI: $50-80"
echo "   - Container Apps: $2-8"
echo "   - Other services: $8-8"
echo ""
echo "🎯 System Status: Ready for production!"