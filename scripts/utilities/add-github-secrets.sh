#!/bin/bash
"""
Simple script to add required GitHub secrets for CI/CD pipeline
Run this script to add secrets from your .env file to GitHub repository
"""

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🔐 Adding GitHub Repository Secrets${NC}"
echo "=========================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found in current directory${NC}"
    exit 1
fi

# Load environment variables
source .env

# Check GitHub CLI
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI not found. Install with:${NC}"
    echo "brew install gh"
    echo "Or visit: https://cli.github.com/"
    exit 1
fi

echo -e "${BLUE}📧 Adding email secrets...${NC}"
echo "$FROM_EMAIL_ADDRESS" | gh secret set FROM_EMAIL_ADDRESS
echo "$WEBDE_APP_PASSWORD" | gh secret set WEBDE_APP_PASSWORD

echo -e "${BLUE}☁️  Adding Azure secrets...${NC}"
echo "$AZURE_SUBSCRIPTION_ID" | gh secret set AZURE_SUBSCRIPTION_ID
echo "$AZURE_TENANT_ID" | gh secret set AZURE_TENANT_ID
echo "$AZURE_RESOURCE_GROUP" | gh secret set AZURE_RESOURCE_GROUP
echo "$AZURE_AI_ENDPOINT" | gh secret set AZURE_AI_ENDPOINT
echo "$AZURE_AI_API_KEY" | gh secret set AZURE_AI_API_KEY

echo -e "${YELLOW}⚠️  AZURE_CREDENTIALS secret needs to be created manually${NC}"
echo "This requires a Service Principal. Run the following command:"
echo ""
echo -e "${BLUE}az ad sp create-for-rbac --name \"github-actions-jasmin\" --role contributor --scopes \"/subscriptions/$AZURE_SUBSCRIPTION_ID\" --sdk-auth${NC}"
echo ""
echo "Then add the output as AZURE_CREDENTIALS secret in GitHub"

echo -e "${GREEN}✅ Basic secrets added successfully!${NC}"
echo ""
echo "📋 Check your secrets at:"
echo "https://github.com/$(gh repo view --json owner,name | jq -r '.owner.login')/$(gh repo view --json owner,name | jq -r '.name')/settings/secrets/actions"