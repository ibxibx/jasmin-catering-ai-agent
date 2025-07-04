# Azure Cloud Architecture - Cost-Effective Deployment

## 🎯 Current Problem
- Everything runs locally only
- No cloud automation or scaling
- Manual execution required
- No 24/7 availability

## 💡 Proposed Cloud Architecture

### **Option 1: Azure Functions + Logic Apps (Recommended)**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Logic App     │───▶│  Azure Function  │───▶│   Slack API     │
│ (Email Trigger) │    │   (main.py)      │    │ (Notifications) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       ▲
         ▼                       ▼                       │
┌─────────────────┐    ┌──────────────────┐              │
│   IMAP/SMTP     │    │  Azure OpenAI    │              │
│  (Email Check)  │    │   (GPT-4o)       │──────────────┘
└─────────────────┘    └──────────────────┘
                                │
                                ▼
                     ┌──────────────────┐
                     │   Key Vault      │
                     │ (All Secrets)    │
                     └──────────────────┘
```

### **Monthly Cost Estimate:**
- **Azure Functions**: ~$5-15/month (Consumption plan)
- **Logic Apps**: ~$10-20/month (Standard workflow)
- **Azure OpenAI**: ~$50-100/month (existing)
- **Key Vault**: ~$3/month (existing)
- **Total: ~$68-138/month**

### **Option 2: Container Apps (Ultra Low Cost)**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Container App  │───▶│    Cron Job      │───▶│   Slack API     │
│   (main.py)     │    │ (Every 5 min)    │    │ (Notifications) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       
         ▼                       
┌─────────────────────────────────────────────────────────────────┐
│                     External Services                          │
│  ┌─────────────────┐    ┌──────────────────┐                  │
│  │   IMAP/SMTP     │    │  Azure OpenAI    │                  │
│  │  (Email Check)  │    │   (GPT-4o)       │                  │
│  └─────────────────┘    └──────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```

### **Monthly Cost Estimate:**
- **Container Apps**: ~$0-5/month (0.25 vCPU, minimal usage)
- **Azure OpenAI**: ~$50-100/month (existing)
- **Key Vault**: ~$3/month (existing)
- **Total: ~$53-108/month**

## 🚀 Implementation Plan

### **Phase 1: Containerize Application**
1. Create Dockerfile for Python app
2. Build container with all dependencies
3. Test locally with Docker

### **Phase 2: Deploy to Azure**
1. Create Container App or Function App
2. Configure environment variables from Key Vault
3. Set up automated triggers (cron/timer)

### **Phase 3: Configure Monitoring**
1. Application Insights integration
2. Slack alerting for failures
3. Cost monitoring and alerts

## 📋 Detailed Implementation

### **1. Dockerfile Creation**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

### **2. Azure Container Apps Deployment**
```bash
# Create Container App
az containerapp create \
  --name jasmin-catering-app \
  --resource-group logicapp-jasmin-sweden_group \
  --environment jasmin-env \
  --image jasmin-catering:latest \
  --min-replicas 0 \
  --max-replicas 1 \
  --cpu 0.25 \
  --memory 0.5Gi
```

### **3. Scheduled Execution**
```yaml
# Container App with cron trigger
scale:
  minReplicas: 0
  maxReplicas: 1
  rules:
  - name: cron-scale
    type: cron
    metadata:
      timezone: "Europe/Berlin"
      start: "0 */5 * * *"  # Every 5 minutes
      end: "59 */5 * * *"
```

## 💰 Cost Comparison

| Component | Local | Functions | Container Apps |
|-----------|-------|-----------|----------------|
| Compute | $0 | $5-15/mo | $0-5/mo |
| Triggers | $0 | $10-20/mo | $0 |
| OpenAI | $50-100/mo | $50-100/mo | $50-100/mo |
| Storage | $0 | $1-2/mo | $1-2/mo |
| **Total** | **$50-100/mo** | **$66-137/mo** | **$51-107/mo** |

## 🎯 Recommendation: Container Apps

**Why Container Apps?**
- ✅ Lowest cost ($0-5/month compute)
- ✅ Built-in scaling to zero
- ✅ Cron job scheduling included
- ✅ Easy deployment from existing code
- ✅ Full control over execution environment
- ✅ Integrated with Azure services

**Next Steps:**
1. Create Dockerfile and requirements.txt
2. Build and test container locally
3. Deploy to Azure Container Apps
4. Configure Key Vault integration
5. Set up cron schedule for email processing
6. Add monitoring and alerting

This approach gives you full cloud automation while keeping costs minimal!