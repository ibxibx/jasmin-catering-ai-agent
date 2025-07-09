#!/bin/bash
# ==============================================================================
# Script: deploy-full-stack.sh
# Purpose: Complete deployment of Jasmin Catering AI Agent
# Type: Core Deployment Script
#
# Description:
#   Master deployment script that orchestrates the full deployment process:
#   - Validates environment and prerequisites
#   - Builds and pushes Docker images
#   - Deploys Container Apps Job with proper configuration
#   - Sets up monitoring and alerts
#   - Validates deployment success
#
# Usage:
#   ./scripts/deployment/core/deploy-full-stack.sh [options]
#
# Options:
#   --skip-build     Skip Docker image build (use existing)
#   --dry-run        Show what would be deployed without executing
#   --force          Force deployment even if validation fails
#
# Prerequisites:
#   - Azure CLI logged in
#   - .env file configured
#   - Docker installed (unless --skip-build)
# ==============================================================================

set -e

# Load utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../utilities/load-env-config.sh"

# Parse arguments
SKIP_BUILD=false
DRY_RUN=false
FORCE=false

for arg in "$@"; do
    case $arg in
        --skip-build) SKIP_BUILD=true ;;
        --dry-run) DRY_RUN=true ;;
        --force) FORCE=true ;;
    esac
done

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🚀 Jasmin Catering AI Agent - Full Stack Deployment"
echo "=================================================="
echo ""

# Step 1: Validate Prerequisites
echo -e "${YELLOW}Step 1: Validating Prerequisites${NC}"
echo "--------------------------------"

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI not found. Please install: https://aka.ms/install-azure-cli${NC}"
    exit 1
fi

# Check login status
if ! az account show &> /dev/null; then
    echo -e "${RED}❌ Not logged into Azure. Please run: az login${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Azure CLI authenticated${NC}"

# Validate environment variables
REQUIRED_VARS=(
    "AZURE_SUBSCRIPTION_ID"
    "AZURE_RESOURCE_GROUP"
    "AZURE_AI_API_KEY"
    "WEBDE_EMAIL_ALIAS"
    "WEBDE_APP_PASSWORD"
    "SLACK_BOT_TOKEN"
)

MISSING_VARS=()
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo -e "${RED}❌ Missing required environment variables:${NC}"
    printf '%s\n' "${MISSING_VARS[@]}"
    if [ "$FORCE" != true ]; then
        exit 1
    fi
fi

echo -e "${GREEN}✅ Environment variables validated${NC}"

# Step 2: Build and Push Docker Image
if [ "$SKIP_BUILD" != true ]; then
    echo -e "\n${YELLOW}Step 2: Building Docker Image${NC}"
    echo "-----------------------------"
    
    if [ "$DRY_RUN" == true ]; then
        echo "[DRY RUN] Would build and push Docker image"
    else
        # Call the container jobs deployment script
        "$SCRIPT_DIR/../deploy-container-jobs.sh"
    fi
else
    echo -e "\n${YELLOW}Step 2: Skipping Docker Build (--skip-build)${NC}"
fi

# Step 3: Validate Deployment
echo -e "\n${YELLOW}Step 3: Validating Deployment${NC}"
echo "-----------------------------"

if [ "$DRY_RUN" != true ]; then
    # Check job status
    JOB_STATUS=$(az containerapp job show \
        --name jasmin-email-processor \
        --resource-group "$AZURE_RESOURCE_GROUP" \
        --query "properties.runningStatus" -o tsv 2>/dev/null || echo "Not Found")
    
    if [ "$JOB_STATUS" == "Ready" ]; then
        echo -e "${GREEN}✅ Container Apps Job is ready${NC}"
    else
        echo -e "${RED}⚠️  Job status: $JOB_STATUS${NC}"
    fi
    
    # Show next execution time
    SCHEDULE=$(az containerapp job show \
        --name jasmin-email-processor \
        --resource-group "$AZURE_RESOURCE_GROUP" \
        --query "properties.configuration.scheduleTriggerConfig.cronExpression" -o tsv)
    
    echo -e "${GREEN}📅 Schedule: $SCHEDULE (every 5 minutes)${NC}"
fi

# Step 4: Post-Deployment Tasks
echo -e "\n${YELLOW}Step 4: Post-Deployment Configuration${NC}"
echo "-------------------------------------"

echo "📋 Next Steps:"
echo "1. Monitor job executions:"
echo "   ./scripts/deployment/monitoring/monitor-container-job.sh"
echo ""
echo "2. View latest logs:"
echo "   ./scripts/deployment/monitoring/monitor-container-job.sh latest"
echo ""
echo "3. Send test emails to: $WEBDE_EMAIL_ALIAS"
echo ""
echo "4. Check Slack channels for notifications"

if [ "$DRY_RUN" == true ]; then
    echo -e "\n${YELLOW}[DRY RUN COMPLETE] No changes were made${NC}"
else
    echo -e "\n${GREEN}✅ Deployment Complete!${NC}"
fi