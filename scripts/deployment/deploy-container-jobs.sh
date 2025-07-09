#!/bin/bash
# ==============================================================================
# Script: deploy-container-jobs.sh
# Purpose: Main deployment script for Jasmin Catering AI Agent
# Type: Core Deployment Script
# 
# Description:
#   Deploys the email processing system to Azure Container Apps Jobs with:
#   - Scheduled execution every 5 minutes
#   - AI-powered response generation
#   - Email duplicate prevention (UNSEEN filter + mark as read)
#   - Slack integration for monitoring
#
# Usage:
#   ./scripts/deployment/deploy-container-jobs.sh
#
# Prerequisites:
#   - Azure CLI logged in (az login)
#   - .env file with all required variables
#   - Docker image built and available
#
# Environment Variables Required:
#   - See .env.example for full list
# ==============================================================================

set -e

echo "🚀 Deploying Jasmin Catering AI Agent as Container Apps Job"
echo "=========================================================="

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

# Build and push updated Docker image with enhanced RAG
echo "2. Building and pushing updated Docker image with enhanced RAG..."
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

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

# Delete existing Container App (we're switching to Jobs)
echo "4. Removing old Container App..."
if az containerapp show --name jasmin-catering-app --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Deleting existing Container App..."
    az containerapp delete \
        --name jasmin-catering-app \
        --resource-group $RESOURCE_GROUP \
        --yes
    echo "✅ Old Container App removed"
else
    echo "✅ No existing Container App to remove"
fi

# Create Container Apps Job with cron schedule
echo "5. Creating Container Apps Job with cron scheduling..."
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
        AZURE_CONTAINER_APPS="true"

echo ""
echo "🎉 Deployment Complete!"
echo "======================="
echo "✅ Container Registry: $ACR_NAME.azurecr.io"
echo "✅ Container Apps Job: $JOB_NAME"
echo "✅ Environment: $CONTAINER_APP_ENV"
echo "✅ Schedule: Every 5 minutes (*/5 * * * *)"
echo ""
echo "📊 Monitoring:"
echo "Job Status: az containerapp job show --name $JOB_NAME --resource-group $RESOURCE_GROUP"
echo "Job Executions: az containerapp job execution list --name $JOB_NAME --resource-group $RESOURCE_GROUP"
echo "Job Logs: az containerapp job logs show --name $JOB_NAME --resource-group $RESOURCE_GROUP"
echo ""
echo "💰 Estimated Monthly Cost: ~$2-8 (vs previous $20+)"
echo "⏰ Execution: Every 5 minutes automatically"
echo "🔧 Manual trigger: az containerapp job start --name $JOB_NAME --resource-group $RESOURCE_GROUP"
echo ""
echo "🗑️  Old Logic Apps can now be deleted to save costs!"