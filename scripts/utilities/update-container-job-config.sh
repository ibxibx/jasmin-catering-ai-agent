#!/bin/bash
# Update Container Apps Job to use only new OpenAI configuration

set -e

echo "🔄 Updating Container Apps Job Configuration"
echo "==========================================="

RESOURCE_GROUP="logicapp-jasmin-sweden_group"
JOB_NAME="jasmin-email-processor"
KEY_VAULT_NAME="jasmin-catering-kv"

# Get secrets from Key Vault
echo "📂 Retrieving secrets from Key Vault..."
OPENAI_ENDPOINT=$(az keyvault secret show --vault-name $KEY_VAULT_NAME --name "openai-endpoint" --query "value" -o tsv)
OPENAI_API_KEY=$(az keyvault secret show --vault-name $KEY_VAULT_NAME --name "openai-api-key" --query "value" -o tsv)
WEBDE_APP_PASSWORD=$(az keyvault secret show --vault-name $KEY_VAULT_NAME --name "webde-app-password" --query "value" -o tsv)
SLACK_BOT_TOKEN=$(az keyvault secret show --vault-name $KEY_VAULT_NAME --name "slack-bot-token" --query "value" -o tsv)
SLACK_CHANNEL_ID=$(az keyvault secret show --vault-name $KEY_VAULT_NAME --name "slack-channel-emailrequestsandresponse" --query "value" -o tsv)
SLACK_LOG_CHANNEL_ID=$(az keyvault secret show --vault-name $KEY_VAULT_NAME --name "slack-channel-jasminlogs" --query "value" -o tsv)

echo "✅ Secrets retrieved"

# Update Container Apps Job with new configuration
echo "🔧 Updating Container Apps Job configuration..."
az containerapp job update \
    --name $JOB_NAME \
    --resource-group $RESOURCE_GROUP \
    --env-vars \
        AZURE_OPENAI_ENDPOINT="$OPENAI_ENDPOINT" \
        AZURE_OPENAI_API_KEY="$OPENAI_API_KEY" \
        AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o" \
        FROM_EMAIL_ADDRESS="matthias.buchhorn@web.de" \
        WEBDE_APP_PASSWORD="$WEBDE_APP_PASSWORD" \
        WEBDE_EMAIL_ALIAS="ma3u-test@email.de" \
        SLACK_BOT_TOKEN="$SLACK_BOT_TOKEN" \
        SLACK_CHANNEL_ID="$SLACK_CHANNEL_ID" \
        SLACK_LOG_CHANNEL_ID="$SLACK_LOG_CHANNEL_ID" \
        AZURE_RESOURCE_GROUP="$RESOURCE_GROUP" \
        AZURE_KEY_VAULT_NAME="$KEY_VAULT_NAME" \
        AZURE_CONTAINER_APPS="true" \
    --remove-env-vars \
        AZURE_AI_ENDPOINT \
        AZURE_AI_API_KEY

echo "✅ Container Apps Job updated"

# Verify configuration
echo "📋 Verifying configuration..."
az containerapp job show \
    --name $JOB_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "properties.template.containers[0].env[?contains(name, 'AZURE')].{name:name, value:value}" \
    --output table

echo ""
echo "🎉 Configuration update complete!"
echo ""
echo "📝 Next steps:"
echo "1. Test locally: python main.py"
echo "2. Test in cloud: az containerapp job start --name $JOB_NAME --resource-group $RESOURCE_GROUP"