#!/bin/bash
# Cleanup and redeploy Jasmin Catering with Azure AI Foundry and AI Agents

set -e

echo "🧹 Jasmin Catering Infrastructure Cleanup and Redeployment"
echo "=========================================================="

# Configuration
RESOURCE_GROUP="logicapp-jasmin-sweden_group"
LOCATION="swedencentral"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

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

echo -e "${YELLOW}⚠️  WARNING: This will DELETE all resources in resource group: $RESOURCE_GROUP${NC}"
echo "Resources to be deleted:"
echo "- Container Apps and Jobs"
echo "- Logic Apps"
echo "- Key Vault"
echo "- Container Registry"
echo "- AI Services"
echo ""

if ! confirm "Are you sure you want to continue?"; then
    echo "❌ Operation cancelled"
    exit 1
fi

# Check Azure CLI authentication
echo "1. Checking Azure CLI authentication..."
if ! az account show &> /dev/null; then
    echo "❌ Not logged into Azure CLI. Please run 'az login' first."
    exit 1
fi
echo "✅ Azure CLI authenticated"

# List all resources in the group
echo ""
echo "2. Current resources in $RESOURCE_GROUP:"
az resource list --resource-group $RESOURCE_GROUP --output table

echo ""
if ! confirm "Do you want to delete ALL these resources?"; then
    echo "❌ Operation cancelled"
    exit 1
fi

# Delete the resource group and all its resources
echo ""
echo "3. Deleting resource group and all resources..."
echo -e "${RED}This operation will take several minutes...${NC}"

az group delete \
    --name $RESOURCE_GROUP \
    --yes \
    --no-wait

echo "✅ Resource group deletion initiated"

# Wait for deletion to complete
echo "4. Waiting for deletion to complete..."
while az group exists --name $RESOURCE_GROUP | grep -q true; do
    echo -n "."
    sleep 10
done
echo ""
echo "✅ Resource group deleted successfully"

# Create new resource group
echo ""
echo "5. Creating new resource group..."
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION

echo "✅ Resource group created: $RESOURCE_GROUP"

# Now deploy the new infrastructure
echo ""
echo -e "${GREEN}Starting new deployment with Azure AI Foundry...${NC}"
echo ""

# Run the new deployment script
./deploy-with-ai-foundry.sh

echo ""
echo "🎉 Cleanup and redeployment complete!"