#!/bin/bash
# Setup email tracking storage for preventing duplicate processing

set -e

echo "🚀 Setting up Email Tracking Storage"
echo "====================================="

# Configuration
RESOURCE_GROUP="logicapp-jasmin-sweden_group"
LOCATION="swedencentral"
STORAGE_ACCOUNT_NAME="jasmincateringstorage"
KEY_VAULT_NAME="jasmin-catering-kv"

# Check if Azure CLI is logged in
echo "1. Checking Azure CLI authentication..."
if ! az account show &> /dev/null; then
    echo "❌ Not logged into Azure CLI. Please run 'az login' first."
    exit 1
fi
echo "✅ Azure CLI authenticated"

# Create storage account if it doesn't exist
echo "2. Creating Azure Storage Account..."
if az storage account show --name $STORAGE_ACCOUNT_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "✅ Storage account already exists"
else
    az storage account create \
        --name $STORAGE_ACCOUNT_NAME \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --sku Standard_LRS \
        --kind StorageV2
    echo "✅ Storage account created"
fi

# Get storage connection string
echo "3. Getting storage connection string..."
STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
    --name $STORAGE_ACCOUNT_NAME \
    --resource-group $RESOURCE_GROUP \
    --query connectionString -o tsv)

# Store in Key Vault
echo "4. Storing connection string in Key Vault..."
az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "storage-connection-string" \
    --value "$STORAGE_CONNECTION_STRING" \
    --output none

echo "✅ Connection string stored in Key Vault"

# Create table for email tracking
echo "5. Creating ProcessedEmails table..."
az storage table create \
    --name ProcessedEmails \
    --connection-string "$STORAGE_CONNECTION_STRING" \
    --output none || echo "Table might already exist"

echo ""
echo "✅ Email tracking storage setup complete!"
echo "Storage Account: $STORAGE_ACCOUNT_NAME"
echo "Table: ProcessedEmails"
echo ""
echo "Next steps:"
echo "1. Run: ./deploy-container-jobs-with-tracking.sh"
echo "2. The updated container will track processed emails"