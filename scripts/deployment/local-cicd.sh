#!/bin/bash
"""
Local CI/CD Deployment Script
Alternative to GitHub Actions when Azure Service Principal creation is blocked
"""

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Local CI/CD Deployment${NC}"
echo "=================================================="
echo -e "${BLUE}🕐 Started at: $(date)${NC}"
echo ""

# Configuration
REGISTRY_NAME="jasmincateringregistry"
RESOURCE_GROUP="logicapp-jasmin-sweden_group"
CONTAINER_JOB="jasmin-email-processor"
IMAGE_TAG="local-$(date +%Y%m%d-%H%M)"

echo -e "${BLUE}📋 Configuration:${NC}"
echo "   Registry: $REGISTRY_NAME"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Container Job: $CONTAINER_JOB"
echo "   Image Tag: $IMAGE_TAG"
echo ""

# Check Azure CLI login
echo -e "${BLUE}🔐 Checking Azure authentication...${NC}"
if ! az account show &> /dev/null; then
    echo -e "${RED}❌ Not logged in to Azure${NC}"
    echo "Please run: az login"
    exit 1
fi

ACCOUNT_NAME=$(az account show --query "name" -o tsv)
echo -e "${GREEN}✅ Logged in as: $ACCOUNT_NAME${NC}"
echo ""

# Build and push container
echo -e "${BLUE}🔨 Building and pushing container image...${NC}"
echo "Image: $REGISTRY_NAME.azurecr.io/jasmin-catering-ai:$IMAGE_TAG"

az acr build \
  --registry $REGISTRY_NAME \
  --image jasmin-catering-ai:$IMAGE_TAG \
  --file Dockerfile \
  .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Container build and push successful${NC}"
else
    echo -e "${RED}❌ Container build failed${NC}"
    exit 1
fi
echo ""

# Update Container Apps Job
echo -e "${BLUE}🚀 Updating Container Apps Job...${NC}"
IMAGE_NAME="$REGISTRY_NAME.azurecr.io/jasmin-catering-ai:$IMAGE_TAG"

az containerapp job update \
  --name $CONTAINER_JOB \
  --resource-group $RESOURCE_GROUP \
  --image "$IMAGE_NAME"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Container Apps Job updated successfully${NC}"
else
    echo -e "${RED}❌ Container Apps Job update failed${NC}"
    exit 1
fi
echo ""

# Trigger test execution
echo -e "${BLUE}🧪 Triggering test execution...${NC}"
EXECUTION=$(az containerapp job start \
  --name $CONTAINER_JOB \
  --resource-group $RESOURCE_GROUP \
  --query "name" -o tsv)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Test execution triggered: $EXECUTION${NC}"
else
    echo -e "${YELLOW}⚠️  Test execution failed to trigger${NC}"
fi
echo ""

# Wait for execution to start
echo -e "${BLUE}⏳ Waiting for execution to start...${NC}"
sleep 10

# Show logs
echo -e "${BLUE}📋 Recent logs:${NC}"
echo "=================================================="
az containerapp job logs show \
  --name $CONTAINER_JOB \
  --resource-group $RESOURCE_GROUP \
  --container $CONTAINER_JOB \
  --follow false \
  --tail 20 2>/dev/null || echo "Logs not available yet"

echo ""
echo -e "${GREEN}🎉 Local CI/CD Deployment Complete!${NC}"
echo "=================================================="
echo -e "${BLUE}📊 Summary:${NC}"
echo "   ✅ Image built and pushed: $IMAGE_TAG"
echo "   ✅ Container Apps Job updated"
echo "   ✅ Test execution triggered: $EXECUTION"
echo ""
echo -e "${BLUE}📋 Monitor execution:${NC}"
echo "   az containerapp job logs show --name $CONTAINER_JOB --resource-group $RESOURCE_GROUP --container $CONTAINER_JOB --follow"
echo ""
echo -e "${BLUE}🔄 To run again:${NC}"
echo "   ./scripts/deployment/local-cicd.sh"