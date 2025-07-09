# 🔐 Admin Setup Required: Federated Identity for GitHub Actions

## Issue
User `matthias.buchhorn@web.de` (subscription co-owner) cannot create app registrations due to Entra ID restrictions.

## What Azure Admin Needs to Do

### 1. Create App Registration
```bash
# Create app registration
az ad app create --display-name "jasmin-github-actions-federated" --sign-in-audience "AzureADMyOrg"

# Get the application ID (save this for step 4)
APP_ID=$(az ad app list --display-name "jasmin-github-actions-federated" --query "[0].appId" -o tsv)
echo "Application ID: $APP_ID"

# Get the object ID (needed for federated credentials)
OBJECT_ID=$(az ad app list --display-name "jasmin-github-actions-federated" --query "[0].id" -o tsv)
echo "Object ID: $OBJECT_ID"
```

### 2. Configure Federated Credentials

**For main branch:**
```bash
cat > federated-credential-main.json << EOF
{
  "name": "jasmin-main-branch",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:ma3u/jasmin-catering-ai-agent:ref:refs/heads/main",
  "description": "GitHub Actions for main branch",
  "audiences": ["api://AzureADTokenExchange"]
}
EOF

az ad app federated-credential create --id $OBJECT_ID --parameters federated-credential-main.json
```

**For pull requests:**
```bash
cat > federated-credential-pr.json << EOF
{
  "name": "jasmin-pull-requests",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:ma3u/jasmin-catering-ai-agent:pull_request",
  "description": "GitHub Actions for pull requests",
  "audiences": ["api://AzureADTokenExchange"]
}
EOF

az ad app federated-credential create --id $OBJECT_ID --parameters federated-credential-pr.json
```

### 3. Create Service Principal
```bash
# Create service principal from app registration
az ad sp create --id $APP_ID

# Verify creation
az ad sp show --id $APP_ID --query "displayName"
```

### 4. Provide Information to User
After completing steps 1-3, provide these values to the user:

```
Application ID (Client ID): $APP_ID
Tenant ID: b4b6ea88-f8b8-4539-a42d-b5e46434242b
Subscription ID: 6576090b-36b2-4ba1-94ae-d2f52eed2789
```

The user can then:
1. Add these as GitHub secrets
2. Assign the contributor role to their resource group
3. Update the GitHub Actions workflow

## Alternative: Grant User Permissions
If admin prefers, they can grant the user **Application Administrator** role:
```bash
# Get user object ID
USER_ID=$(az ad user show --id "matthias.buchhorn@web.de" --query "id" -o tsv)

# Assign Application Administrator role
az rest --method POST \
  --uri "https://graph.microsoft.com/v1.0/directoryRoles/roleTemplateId=9b895d92-2cd3-44c7-9d02-a6ac2d5ea5c3/members" \
  --body "{\"@odata.id\": \"https://graph.microsoft.com/v1.0/directoryObjects/$USER_ID\"}"
```

## Repository Details
- **Repository**: ma3u/jasmin-catering-ai-agent
- **Resource Group**: logicapp-jasmin-sweden_group
- **Subscription**: 6576090b-36b2-4ba1-94ae-d2f52eed2789
- **Tenant**: b4b6ea88-f8b8-4539-a42d-b5e46434242b

## Next Steps After Admin Setup
1. User adds GitHub secrets
2. User assigns Azure roles
3. User updates GitHub Actions workflow
4. CI/CD pipeline becomes fully functional