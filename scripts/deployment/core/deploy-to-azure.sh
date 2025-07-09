#!/bin/bash
# Deploy Jasmin Catering AI Agent to Azure Container Apps

set -e

echo "🚀 Deploying Jasmin Catering AI Agent to Azure"
echo "=============================================="

# Configuration
RESOURCE_GROUP="logicapp-jasmin-sweden_group"
LOCATION="swedencentral"
CONTAINER_APP_NAME="jasmin-catering-app"
CONTAINER_APP_ENV="jasmin-catering-env"
ACR_NAME="jasmincateringregistry"
IMAGE_NAME="jasmin-catering-ai"
KEY_VAULT_NAME="jasmin-catering-kv"

# Check if Azure CLI is logged in
echo "1. Checking Azure CLI authentication..."
if ! az account show &> /dev/null; then
    echo "❌ Not logged into Azure CLI. Please run 'az login' first."
    exit 1
fi
echo "✅ Azure CLI authenticated"

# Create Azure Container Registry if not exists
echo "2. Setting up Azure Container Registry..."
if ! az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating Azure Container Registry..."
    az acr create \
        --resource-group $RESOURCE_GROUP \
        --name $ACR_NAME \
        --sku Basic \
        --location $LOCATION
else
    echo "✅ Azure Container Registry already exists"
fi

# Build and push Docker image
echo "3. Building and pushing Docker image..."
az acr build \
    --registry $ACR_NAME \
    --image $IMAGE_NAME:latest \
    --file Dockerfile .

echo "✅ Docker image built and pushed"

# Create Container Apps environment if not exists
echo "4. Setting up Container Apps environment..."
if ! az containerapp env show --name $CONTAINER_APP_ENV --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating Container Apps environment..."
    az containerapp env create \
        --name $CONTAINER_APP_ENV \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION
else
    echo "✅ Container Apps environment already exists"
fi

# Get Key Vault secrets for environment variables
echo "5. Retrieving secrets from Key Vault..."
AZURE_AI_API_KEY=$(az keyvault secret show --vault-name $KEY_VAULT_NAME --name "azure-ai-api-key" --query "value" -o tsv)
WEBDE_APP_PASSWORD=$(az keyvault secret show --vault-name $KEY_VAULT_NAME --name "webde-app-password" --query "value" -o tsv)
SLACK_BOT_TOKEN=$(az keyvault secret show --vault-name $KEY_VAULT_NAME --name "slack-bot-token" --query "value" -o tsv)
SLACK_CHANNEL_ID=$(az keyvault secret show --vault-name $KEY_VAULT_NAME --name "slack-channel-id" --query "value" -o tsv)
SLACK_LOG_CHANNEL_ID=$(az keyvault secret show --vault-name $KEY_VAULT_NAME --name "slack-log-channel-id" --query "value" -o tsv)

# Deploy or update Container App
echo "6. Deploying Container App..."
if az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Updating existing Container App..."
    az containerapp update \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --image "$ACR_NAME.azurecr.io/$IMAGE_NAME:latest" \
        --set-env-vars \
            AZURE_AI_ENDPOINT="https://swedencentral.api.cognitive.microsoft.com" \
            AZURE_AI_API_KEY="$AZURE_AI_API_KEY" \
            FROM_EMAIL_ADDRESS="matthias.buchhorn@web.de" \
            WEBDE_APP_PASSWORD="$WEBDE_APP_PASSWORD" \
            WEBDE_EMAIL_ALIAS="ma3u-test@email.de" \
            SLACK_BOT_TOKEN="$SLACK_BOT_TOKEN" \
            SLACK_CHANNEL_ID="$SLACK_CHANNEL_ID" \
            SLACK_LOG_CHANNEL_ID="$SLACK_LOG_CHANNEL_ID" \
            AZURE_RESOURCE_GROUP="$RESOURCE_GROUP" \
            AZURE_KEY_VAULT_NAME="$KEY_VAULT_NAME"
else
    echo "Creating new Container App..."
    az containerapp create \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --environment $CONTAINER_APP_ENV \
        --image "$ACR_NAME.azurecr.io/$IMAGE_NAME:latest" \
        --target-port 8000 \
        --ingress external \
        --min-replicas 0 \
        --max-replicas 1 \
        --cpu 0.25 \
        --memory 0.5Gi \
        --env-vars \
            AZURE_AI_ENDPOINT="https://swedencentral.api.cognitive.microsoft.com" \
            AZURE_AI_API_KEY="$AZURE_AI_API_KEY" \
            FROM_EMAIL_ADDRESS="matthias.buchhorn@web.de" \
            WEBDE_APP_PASSWORD="$WEBDE_APP_PASSWORD" \
            WEBDE_EMAIL_ALIAS="ma3u-test@email.de" \
            SLACK_BOT_TOKEN="$SLACK_BOT_TOKEN" \
            SLACK_CHANNEL_ID="$SLACK_CHANNEL_ID" \
            SLACK_LOG_CHANNEL_ID="$SLACK_LOG_CHANNEL_ID" \
            AZURE_RESOURCE_GROUP="$RESOURCE_GROUP" \
            AZURE_KEY_VAULT_NAME="$KEY_VAULT_NAME"
fi

# Note: For scheduled execution, use Container Apps Jobs with cron schedule
echo "7. Container Apps Job can be created with cron schedule..."
echo "   Use deploy-container-jobs.sh for scheduled job deployment"

# Container Apps Jobs handle their own scheduling with cron
# No additional scheduler needed

echo ""
echo "🎉 Deployment Complete!"
echo "======================="
echo "✅ Container Registry: $ACR_NAME.azurecr.io"
echo "✅ Container App: $CONTAINER_APP_NAME"
echo "✅ Environment: $CONTAINER_APP_ENV"
echo "✅ Note: Use Container Apps Jobs for scheduling"
echo ""
echo "📊 Monitoring URLs:"
echo "Container App: https://portal.azure.com/#@/resource/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/$CONTAINER_APP_NAME"
echo ""
echo "💰 Estimated Monthly Cost: ~$5-15"
echo "⏰ Execution: Every 5 minutes"
echo ""
echo "🔧 To trigger manually:"
echo "curl -X POST https://$CONTAINER_APP_NAME.${LOCATION}.azurecontainerapps.io/trigger"