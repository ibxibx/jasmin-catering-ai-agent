# 🔐 GitHub Secrets Setup Guide

## ✅ Secrets Already Added

The following secrets have been successfully added to your GitHub repository:

- ✅ `FROM_EMAIL_ADDRESS`
- ✅ `WEBDE_APP_PASSWORD` 
- ✅ `AZURE_SUBSCRIPTION_ID`
- ✅ `AZURE_TENANT_ID`
- ✅ `AZURE_AI_ENDPOINT`
- ✅ `AZURE_AI_API_KEY`

## ⚠️ Missing: AZURE_CREDENTIALS

You need to add the `AZURE_CREDENTIALS` secret manually because it requires Azure admin privileges to create a Service Principal.

### Option 1: Create Service Principal (Requires Admin Access)

If you have Azure admin access, run:

```bash
az ad sp create-for-rbac \
  --name "jasmin-github-actions" \
  --role contributor \
  --scopes "/subscriptions/6576090b-36b2-4ba1-94ae-d2f52eed2789" \
  --sdk-auth
```

### Option 2: Ask Azure Admin

Send this to your Azure administrator:

**Subject**: Create Service Principal for GitHub Actions - Jasmin Catering

**Message**:
```
Hi,

I need a Service Principal created for GitHub Actions CI/CD deployment of the Jasmin Catering AI system.

Please run this command:

az ad sp create-for-rbac \
  --name "jasmin-github-actions" \
  --role contributor \
  --scopes "/subscriptions/6576090b-36b2-4ba1-94ae-d2f52eed2789" \
  --sdk-auth

Then share the JSON output (securely) so I can add it as AZURE_CREDENTIALS secret in GitHub.

Resource Group: logicapp-jasmin-sweden_group
Services: Container Apps, Container Registry, Key Vault

Thanks!
```

### Option 3: Manual GitHub Secret Addition

1. Go to: https://github.com/ma3u/jasmin-catering-ai-agent/settings/secrets/actions
2. Click "New repository secret"
3. Name: `AZURE_CREDENTIALS`
4. Value: JSON format like this:

```json
{
  "clientId": "your-service-principal-client-id",
  "clientSecret": "your-service-principal-client-secret",
  "subscriptionId": "6576090b-36b2-4ba1-94ae-d2f52eed2789",
  "tenantId": "b4b6ea88-f8b8-4539-a42d-b5e46434242b"
}
```

## 🚀 Test the Pipeline

Once `AZURE_CREDENTIALS` is added:

1. Push any change to the `main` branch
2. Watch GitHub Actions run: https://github.com/ma3u/jasmin-catering-ai-agent/actions
3. The pipeline will:
   - Build Docker image
   - Push to Azure Container Registry
   - Deploy to Container Apps
   - Send test email to ma3u-test@email.de
   - Verify email processing
   - Generate test report

## 📋 Current Secrets Status

| Secret | Status | Purpose |
|--------|--------|---------|
| `FROM_EMAIL_ADDRESS` | ✅ Added | Email authentication |
| `WEBDE_APP_PASSWORD` | ✅ Added | Email password |
| `AZURE_SUBSCRIPTION_ID` | ✅ Added | Azure subscription |
| `AZURE_TENANT_ID` | ✅ Added | Azure tenant |
| `AZURE_AI_ENDPOINT` | ✅ Added | AI service endpoint |
| `AZURE_AI_API_KEY` | ✅ Added | AI service key |
| `AZURE_CREDENTIALS` | ❌ **MISSING** | Service Principal for deployment |

## 🔗 Useful Links

- **Repository Secrets**: https://github.com/ma3u/jasmin-catering-ai-agent/settings/secrets/actions
- **GitHub Actions**: https://github.com/ma3u/jasmin-catering-ai-agent/actions
- **Azure Portal**: https://portal.azure.com/#@b4b6ea88-f8b8-4539-a42d-b5e46434242b/resource/subscriptions/6576090b-36b2-4ba1-94ae-d2f52eed2789/resourceGroups/logicapp-jasmin-sweden_group/overview