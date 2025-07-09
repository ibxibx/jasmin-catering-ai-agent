# 🚀 Simplified Deployment Without GitHub Actions

If Azure admin privileges are not available, we can use alternative deployment strategies.

## Option 1: Manual Container Build & Deploy
```bash
# Build and push manually (you have ACR push permissions)
az acr build --registry jasmincateringregistry --image jasmin-catering-ai:manual-$(date +%Y%m%d-%H%M) .

# Update Container Apps Job manually  
az containerapp job update \
  --name jasmin-email-processor \
  --resource-group logicapp-jasmin-sweden_group \
  --image "jasmincateringregistry.azurecr.io/jasmin-catering-ai:manual-$(date +%Y%m%d-%H%M)"
```

## Option 2: Local CI/CD Script
Create a local script that does the same as GitHub Actions:

```bash
#!/bin/bash
# scripts/deployment/local-cicd.sh

set -e

echo "🚀 Local CI/CD Deployment"
echo "=========================="

# Build and push
IMAGE_TAG="local-$(date +%Y%m%d-%H%M)"
echo "Building image: $IMAGE_TAG"

az acr build \
  --registry jasmincateringregistry \
  --image jasmin-catering-ai:$IMAGE_TAG \
  .

# Deploy
echo "Deploying to Container Apps..."
az containerapp job update \
  --name jasmin-email-processor \
  --resource-group logicapp-jasmin-sweden_group \
  --image "jasmincateringregistry.azurecr.io/jasmin-catering-ai:$IMAGE_TAG"

# Test
echo "Triggering test execution..."
az containerapp job start \
  --name jasmin-email-processor \
  --resource-group logicapp-jasmin-sweden_group

echo "✅ Deployment complete!"
echo "Monitor logs: az containerapp job logs show --name jasmin-email-processor --resource-group logicapp-jasmin-sweden_group --container jasmin-email-processor"
```

## Option 3: Container Apps Managed Identity for Runtime
For the Container Apps Job itself (not GitHub Actions), you can use Managed Identity:

```bash
# Enable managed identity on Container Apps Job
az containerapp job identity assign \
  --name jasmin-email-processor \
  --resource-group logicapp-jasmin-sweden_group \
  --system-assigned

# Get the managed identity principal ID
PRINCIPAL_ID=$(az containerapp job show \
  --name jasmin-email-processor \
  --resource-group logicapp-jasmin-sweden_group \
  --query "identity.principalId" -o tsv)

# Assign Key Vault access (if needed for secrets)
az keyvault set-policy \
  --name jasmin-catering-kv \
  --object-id $PRINCIPAL_ID \
  --secret-permissions get list
```

## Recommended Approach
1. **For now**: Use manual deployment script (Option 2)
2. **Later**: Setup federated identity when possible
3. **Production**: Container Apps Job can use managed identity for Azure resources