#!/bin/bash
"""
Script to add GitHub repository secrets for CI/CD pipeline
Reads from .env file and adds required secrets to GitHub repository
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔐 Setting up GitHub Repository Secrets${NC}"
echo "=================================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo "Please ensure .env file exists in the project root"
    exit 1
fi

# Load environment variables from .env
source .env

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) not found${NC}"
    echo "Please install GitHub CLI: https://cli.github.com/"
    echo "Then run: gh auth login"
    exit 1
fi

# Check if user is authenticated with GitHub
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not authenticated with GitHub${NC}"
    echo "Please run: gh auth login"
    exit 1
fi

# Get repository information
REPO_INFO=$(gh repo view --json owner,name)
REPO_OWNER=$(echo $REPO_INFO | jq -r '.owner.login')
REPO_NAME=$(echo $REPO_INFO | jq -r '.name')

echo -e "${BLUE}📁 Repository: ${REPO_OWNER}/${REPO_NAME}${NC}"
echo ""

# Function to add secret to GitHub
add_github_secret() {
    local secret_name=$1
    local secret_value=$2
    local description=$3
    
    if [ -z "$secret_value" ]; then
        echo -e "${YELLOW}⚠️  Skipping ${secret_name} (empty value)${NC}"
        return
    fi
    
    echo -e "${BLUE}🔑 Adding secret: ${secret_name}${NC}"
    echo "   Description: $description"
    
    # Add secret to GitHub repository
    echo "$secret_value" | gh secret set "$secret_name" --body -
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Successfully added ${secret_name}${NC}"
    else
        echo -e "${RED}❌ Failed to add ${secret_name}${NC}"
    fi
    echo ""
}

# Function to create Azure service principal credentials
create_azure_credentials() {
    echo -e "${BLUE}🔐 Creating Azure Service Principal for GitHub Actions${NC}"
    echo ""
    
    # Check if Azure CLI is installed and user is logged in
    if ! command -v az &> /dev/null; then
        echo -e "${RED}❌ Azure CLI not found${NC}"
        echo "Please install Azure CLI and run: az login"
        return 1
    fi
    
    if ! az account show &> /dev/null; then
        echo -e "${YELLOW}⚠️  Not logged in to Azure${NC}"
        echo "Please run: az login"
        return 1
    fi
    
    # Create service principal with contributor role
    echo "Creating service principal for subscription: $AZURE_SUBSCRIPTION_ID"
    
    SP_OUTPUT=$(az ad sp create-for-rbac \
        --name "github-actions-jasmin-catering" \
        --role contributor \
        --scopes "/subscriptions/$AZURE_SUBSCRIPTION_ID" \
        --sdk-auth 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Service principal created successfully${NC}"
        echo ""
        
        # Add Azure credentials to GitHub secrets
        add_github_secret "AZURE_CREDENTIALS" "$SP_OUTPUT" "Azure service principal credentials for GitHub Actions"
        
        echo -e "${BLUE}📋 Service Principal Details:${NC}"
        echo "   Name: github-actions-jasmin-catering"
        echo "   Role: Contributor"
        echo "   Scope: /subscriptions/$AZURE_SUBSCRIPTION_ID"
        echo ""
    else
        echo -e "${RED}❌ Failed to create service principal${NC}"
        echo "You may need to create it manually or ask an Azure admin"
        echo ""
        
        # Provide manual instructions
        echo -e "${YELLOW}📋 Manual AZURE_CREDENTIALS format:${NC}"
        cat << EOF
{
  "clientId": "your-service-principal-client-id",
  "clientSecret": "your-service-principal-client-secret",
  "subscriptionId": "$AZURE_SUBSCRIPTION_ID",
  "tenantId": "$AZURE_TENANT_ID"
}
EOF
        echo ""
    fi
}

echo -e "${BLUE}🚀 Starting GitHub Secrets Setup${NC}"
echo ""

# Create Azure service principal first
create_azure_credentials

# Add required secrets for GitHub Actions CI/CD
echo -e "${BLUE}📧 Adding Email Configuration Secrets${NC}"
add_github_secret "FROM_EMAIL_ADDRESS" "$FROM_EMAIL_ADDRESS" "Email address for sending test emails"
add_github_secret "WEBDE_APP_PASSWORD" "$WEBDE_APP_PASSWORD" "Web.de app password for email authentication"

echo -e "${BLUE}⚙️  Adding Azure Configuration Secrets${NC}"
add_github_secret "AZURE_SUBSCRIPTION_ID" "$AZURE_SUBSCRIPTION_ID" "Azure subscription ID"
add_github_secret "AZURE_TENANT_ID" "$AZURE_TENANT_ID" "Azure tenant ID"
add_github_secret "AZURE_RESOURCE_GROUP" "$AZURE_RESOURCE_GROUP" "Azure resource group name"

echo -e "${BLUE}🤖 Adding AI Service Secrets${NC}"
add_github_secret "AZURE_AI_ENDPOINT" "$AZURE_AI_ENDPOINT" "Azure AI service endpoint"
add_github_secret "AZURE_AI_API_KEY" "$AZURE_AI_API_KEY" "Azure AI service API key"

# List all secrets (without values for security)
echo -e "${BLUE}📋 Repository Secrets Summary${NC}"
echo "============================================"
gh secret list
echo ""

echo -e "${GREEN}🎉 GitHub Secrets Setup Complete!${NC}"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo "1. Verify all secrets are correctly set in GitHub repository settings"
echo "2. Push to main branch to trigger the CI/CD pipeline"
echo "3. Monitor GitHub Actions for successful build and deployment"
echo "4. Check the automated test results in the workflow"
echo ""
echo -e "${YELLOW}🔗 Repository Secrets URL:${NC}"
echo "https://github.com/${REPO_OWNER}/${REPO_NAME}/settings/secrets/actions"
echo ""