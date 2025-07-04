# 🚀 Azure Cloud Deployment Guide

## 📋 Overview

This guide will deploy your Jasmin Catering AI Agent to Azure Container Apps for **$5-15/month** with full cloud automation.

### 🏗️ Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Logic App     │───▶│ Container App    │───▶│   Slack API     │
│ (5min trigger)  │    │   (main.py)      │    │ (Notifications) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                     ┌──────────────────┐
                     │  Azure Services  │
                     │ • OpenAI (GPT-4o)│
                     │ • Key Vault      │
                     │ • Container Reg  │
                     └──────────────────┘
```

## 🚀 Quick Deployment

### Prerequisites
```bash
# 1. Azure CLI installed and logged in
az login

# 2. Docker installed (for building image)
docker --version

# 3. Current directory should be project root
cd /path/to/jasmin-catering-ai-agent
```

### One-Command Deployment
```bash
./deploy-to-azure.sh
```

This script will:
- ✅ Create Azure Container Registry
- ✅ Build and push Docker image
- ✅ Create Container Apps environment
- ✅ Deploy container with environment variables
- ✅ Set up Logic App scheduler (every 5 minutes)
- ✅ Configure all Azure services

## 📊 Cost Breakdown

| Service | Monthly Cost | Purpose |
|---------|-------------|---------|
| Container Apps | $0-5 | Hosting (0.25 vCPU, scale to zero) |
| Logic Apps | $5-10 | Scheduling (5min intervals) |
| Container Registry | $5 | Image storage |
| OpenAI Service | $50-100 | AI responses (existing) |
| Key Vault | $3 | Secret storage (existing) |
| **Total** | **$63-123** | **vs $50-100 local** |

## 🎯 Features Gained

### ✅ Cloud Benefits
- **24/7 Availability** - No local machine required
- **Auto-scaling** - Scale to zero when not in use
- **Monitoring** - Built-in Azure monitoring
- **Security** - Managed secrets in Key Vault
- **Reliability** - Azure SLA guarantees

### 🔧 How It Works
1. **Timer Trigger** - Logic App triggers every 5 minutes
2. **HTTP Call** - Calls Container App `/trigger` endpoint
3. **Email Processing** - Container executes main.py workflow
4. **Slack Notification** - Results posted to Slack channels
5. **Scale Down** - Container scales to zero after execution

## 📱 Monitoring & Management

### Azure Portal URLs
After deployment, access:
- **Container App**: [Azure Portal Container Apps](https://portal.azure.com)
- **Logic App**: Search "jasmin-catering-scheduler"
- **Container Registry**: Search "jasmincateringregistry"

### Manual Triggers
```bash
# Trigger processing manually
curl -X POST https://jasmin-catering-app.swedencentral.azurecontainerapps.io/trigger

# Health check
curl https://jasmin-catering-app.swedencentral.azurecontainerapps.io/health
```

### Logs & Debugging
```bash
# View container logs
az containerapp logs show \
  --name jasmin-catering-app \
  --resource-group logicapp-jasmin-sweden_group

# View Logic App runs
az logic workflow list-runs \
  --resource-group logicapp-jasmin-sweden_group \
  --name jasmin-catering-scheduler
```

## 🔧 Configuration

### Environment Variables (Auto-configured)
- `AZURE_AI_ENDPOINT` - OpenAI service endpoint
- `AZURE_AI_API_KEY` - From Key Vault
- `WEBDE_APP_PASSWORD` - Email password from Key Vault
- `SLACK_BOT_TOKEN` - Slack integration from Key Vault
- `SLACK_CHANNEL_ID` - Email channel ID
- `SLACK_LOG_CHANNEL_ID` - Log channel ID
- `AZURE_CONTAINER_APPS=true` - Enables HTTP server mode

### Updating Configuration
```bash
# Update environment variables
az containerapp update \
  --name jasmin-catering-app \
  --resource-group logicapp-jasmin-sweden_group \
  --set-env-vars NEW_VAR="new_value"

# Update schedule (Logic App)
# Edit in Azure Portal: Logic Apps > jasmin-catering-scheduler > Logic app designer
```

## 🚨 Troubleshooting

### Common Issues

**Container Won't Start**
```bash
# Check logs
az containerapp logs show --name jasmin-catering-app --resource-group logicapp-jasmin-sweden_group

# Check environment variables
az containerapp show --name jasmin-catering-app --resource-group logicapp-jasmin-sweden_group --query "properties.template.containers[0].env"
```

**Secrets Not Loading**
```bash
# Verify Key Vault access
az keyvault secret list --vault-name jasmin-catering-kv

# Check secret values
az keyvault secret show --vault-name jasmin-catering-kv --name slack-bot-token
```

**Schedule Not Working**
```bash
# Check Logic App status
az logic workflow show --resource-group logicapp-jasmin-sweden_group --name jasmin-catering-scheduler --query "state"

# View recent runs
az logic workflow list-runs --resource-group logicapp-jasmin-sweden_group --name jasmin-catering-scheduler
```

## 🔄 Updates & Maintenance

### Deploy New Version
```bash
# Build new image
az acr build --registry jasmincateringregistry --image jasmin-catering-ai:latest --file Dockerfile .

# Update container app (auto-pulls latest)
az containerapp update --name jasmin-catering-app --resource-group logicapp-jasmin-sweden_group
```

### Stop/Start Service
```bash
# Stop (scale to 0)
az containerapp update --name jasmin-catering-app --resource-group logicapp-jasmin-sweden_group --min-replicas 0 --max-replicas 0

# Start (restore scaling)
az containerapp update --name jasmin-catering-app --resource-group logicapp-jasmin-sweden_group --min-replicas 0 --max-replicas 1
```

## 🎉 Success Indicators

After deployment, you should see:
- ✅ Container App running and healthy
- ✅ Logic App triggering every 5 minutes
- ✅ Slack notifications for email processing
- ✅ Azure Monitor showing container metrics
- ✅ Estimated cost: $5-15/month for compute

Your Jasmin Catering AI Agent is now fully cloud-native! 🚀