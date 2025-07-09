#!/bin/bash
# Deploy Jasmin Catering AI Agent with Email Tracking

set -e

echo "🚀 Deploying Jasmin Catering AI Agent with Email Tracking"
echo "========================================================="

# Configuration
RESOURCE_GROUP="logicapp-jasmin-sweden_group"
LOCATION="swedencentral"
JOB_NAME="jasmin-email-processor"
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

# Build and push updated Docker image with email tracking
echo "2. Building and pushing Docker image with email tracking..."
az acr build \
    --registry $ACR_NAME \
    --image $IMAGE_NAME:latest \
    --file Dockerfile .

echo "✅ Docker image updated and pushed"

# Get secrets from Key Vault
echo "3. Retrieving secrets from Key Vault..."
OPENAI_API_KEY=$(az keyvault secret show --vault-name $KEY_VAULT_NAME --name "openai-api-key" --query "value" -o tsv)
OPENAI_ENDPOINT=$(az keyvault secret show --vault-name $KEY_VAULT_NAME --name "openai-endpoint" --query "value" -o tsv)
WEBDE_APP_PASSWORD=$(az keyvault secret show --vault-name $KEY_VAULT_NAME --name "webde-app-password" --query "value" -o tsv)
SLACK_BOT_TOKEN=$(az keyvault secret show --vault-name $KEY_VAULT_NAME --name "slack-bot-token" --query "value" -o tsv)
SLACK_CHANNEL_ID=$(az keyvault secret show --vault-name $KEY_VAULT_NAME --name "slack-channel-emailrequestsandresponse" --query "value" -o tsv)
SLACK_LOG_CHANNEL_ID=$(az keyvault secret show --vault-name $KEY_VAULT_NAME --name "slack-channel-jasminlogs" --query "value" -o tsv)
STORAGE_CONNECTION_STRING=$(az keyvault secret show --vault-name $KEY_VAULT_NAME --name "storage-connection-string" --query "value" -o tsv || echo "")

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

# Delete existing job to update it
echo "4. Updating Container Apps Job..."
if az containerapp job show --name $JOB_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Deleting existing job to update configuration..."
    az containerapp job delete \
        --name $JOB_NAME \
        --resource-group $RESOURCE_GROUP \
        --yes
fi

# Create Container Apps Job with email tracking
echo "5. Creating Container Apps Job with email tracking..."
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
        AZURE_OPENAI_API_KEY="$OPENAI_API_KEY" \
        AZURE_AI_ENDPOINT="$OPENAI_ENDPOINT" \
        AZURE_AI_API_KEY="$OPENAI_API_KEY" \
        FROM_EMAIL_ADDRESS="matthias.buchhorn@web.de" \
        WEBDE_APP_PASSWORD="$WEBDE_APP_PASSWORD" \
        WEBDE_EMAIL_ALIAS="ma3u-test@email.de" \
        SLACK_BOT_TOKEN="$SLACK_BOT_TOKEN" \
        SLACK_CHANNEL_ID="$SLACK_CHANNEL_ID" \
        SLACK_LOG_CHANNEL_ID="$SLACK_LOG_CHANNEL_ID" \
        AZURE_RESOURCE_GROUP="$RESOURCE_GROUP" \
        AZURE_KEY_VAULT_NAME="$KEY_VAULT_NAME" \
        AZURE_CONTAINER_APPS="true" \
        AZURE_STORAGE_CONNECTION_STRING="$STORAGE_CONNECTION_STRING"

echo ""
echo "🎉 Deployment Complete with Email Tracking!"
echo "=========================================="
echo "✅ Container Registry: $ACR_NAME.azurecr.io"
echo "✅ Container Apps Job: $JOB_NAME"
echo "✅ Environment: $CONTAINER_APP_ENV"
echo "✅ Schedule: Every 5 minutes (*/5 * * * *)"
echo "✅ Email Tracking: Enabled (prevents duplicate responses)"
echo ""
echo "📊 Monitoring:"
echo "Job Status: az containerapp job show --name $JOB_NAME --resource-group $RESOURCE_GROUP"
echo "Job Executions: az containerapp job execution list --name $JOB_NAME --resource-group $RESOURCE_GROUP"
echo "Job Logs: az containerapp job logs show --name $JOB_NAME --resource-group $RESOURCE_GROUP --container $JOB_NAME"
echo ""
echo "⚠️  IMPORTANT: Each email will now only be processed ONCE!"
echo "✅ No more duplicate responses to the same email"