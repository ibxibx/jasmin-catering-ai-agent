# 🔐 Setup Federated Identity for GitHub Actions (No Service Principal Required)

## Overview
Instead of creating a Service Principal (which requires admin privileges), we can use **Workload Identity Federation**. This allows GitHub Actions to authenticate with Azure using OpenID Connect (OIDC) without storing long-lived secrets.

## Benefits
- ✅ **No Service Principal required**
- ✅ **No long-lived secrets in GitHub**
- ✅ **More secure** (short-lived tokens)
- ✅ **Works with existing permissions**

## Setup Steps

### 1. Create App Registration (Lower Privileges Required)
```bash
# Create app registration (you might have permission for this)
az ad app create --display-name "jasmin-github-actions-federated"

# Get the application ID
APP_ID=$(az ad app list --display-name "jasmin-github-actions-federated" --query "[0].appId" -o tsv)
echo "App ID: $APP_ID"

# Get the object ID
OBJECT_ID=$(az ad app list --display-name "jasmin-github-actions-federated" --query "[0].id" -o tsv)
echo "Object ID: $OBJECT_ID"
```

### 2. Configure Federated Credentials
```bash
# Create federated credential for main branch
cat > federated-credential.json << EOF
{
  "name": "jasmin-main-branch",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:ma3u/jasmin-catering-ai-agent:ref:refs/heads/main",
  "description": "GitHub Actions for main branch",
  "audiences": ["api://AzureADTokenExchange"]
}
EOF

# Add federated credential
az ad app federated-credential create --id $OBJECT_ID --parameters federated-credential.json
```

### 3. Assign Azure Roles (You likely have permission for this)
```bash
# Create service principal from app registration
az ad sp create --id $APP_ID

# Assign contributor role to your resource group
az role assignment create \
  --assignee $APP_ID \
  --role contributor \
  --scope "/subscriptions/6576090b-36b2-4ba1-94ae-d2f52eed2789/resourceGroups/logicapp-jasmin-sweden_group"
```

### 4. GitHub Repository Settings
Add these secrets to GitHub (no sensitive values needed):

```bash
# Client ID (not sensitive)
AZURE_CLIENT_ID=$APP_ID

# Tenant ID (not sensitive) 
AZURE_TENANT_ID=b4b6ea88-f8b8-4539-a42d-b5e46434242b

# Subscription ID (not sensitive)
AZURE_SUBSCRIPTION_ID=6576090b-36b2-4ba1-94ae-d2f52eed2789
```

## Updated GitHub Actions Workflow

Replace the azure/login step with:

```yaml
- name: Log in to Azure using OIDC
  uses: azure/login@v1
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

## Why This Works
1. **App Registration**: Lower privilege requirement than Service Principal
2. **Federated Identity**: No secrets stored, uses GitHub's OIDC tokens
3. **Resource-Scoped**: Only access to your specific resource group
4. **Temporary Tokens**: More secure than long-lived secrets