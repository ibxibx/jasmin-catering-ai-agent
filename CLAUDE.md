# CLAUDE.md - Guide for Future Claude Instances

This file provides essential guidance for Claude Code when working with the Jasmin Catering AI Agent codebase.

## 🎯 Project Overview

**What**: Automated catering inquiry processing system for Jasmin Catering (Syrian fusion restaurant in Berlin)
**Current Status**: Deployed to Sweden Central, monitoring emails at `ma3u-test@email.de`
**Technology**: Azure Container Apps + Azure AI Foundry Assistants + CLI deployment

## 🚨 Critical Information

### 1. **Region: Sweden Central**
- **ALWAYS use `swedencentral`** - West Europe is NOT accepting new customers
- Default region set in `load-env-config.sh`
- Resource group: `logicapp-jasmin-sweden_group`

### 2. **Deployment Philosophy**
- **NO manual Azure Portal configuration** - Everything must be scriptable
- Use `az` CLI commands only (avoid `azd` due to interactive prompts)
- All secrets in `.env` file - NEVER hardcode

### 3. **Email Configuration**
- Filter emails by TO field: `ma3u-test@email.de`
- App password: Stored in `.env` as `WEBDE_APP_PASSWORD`
- Only process emails sent TO this alias (not FROM)

### 4. **AI Service: Azure AI Foundry with Assistants**
- Using **Azure AI Foundry** with Assistants API
- Assistant ID: `asst_UHTUDffJEyLQ6qexElqOopac`
- Vector Store ID: `vs_xDbEaqnBNUtJ70P7GoNgY1qD`
- Model: GPT-4o
- SDK: Azure AI SDK for Python
- Docs: https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents-readme?view=azure-python

## 📁 Project Structure

```
jasmin-catering-ai-agent/
├── .env                           # ALL secrets here (never commit!)
├── CLAUDE.md                      # This file
├── README.md                      # Main documentation
├── deployments/                   # All deployment assets
│   ├── scripts/                   # Deployment scripts
│   │   ├── deploy-main.sh        # Main deployment
│   │   ├── load-env-config.sh    # Environment loader
│   │   └── monitor-logic-app.sh  # Monitoring
│   ├── logic-apps/               # Workflow definitions
│   │   └── email-processor-workflow.json
│   └── templates/                # Email templates
│       └── email-draft-example.md
```

## 🔧 Common Tasks

### Deploy the System
```bash
cd scripts/deployment
./deploy-container-jobs.sh
```

### Monitor Container Apps Job
```bash
# Check recent executions
az containerapp job list --name jasmin-email-processor --resource-group jasmin-catering-rg

# View logs for specific execution
az containerapp job logs show --name jasmin-email-processor --resource-group jasmin-catering-rg
```

## ⚠️ Known Issues & Solutions

### 1. Region Restrictions
**Problem**: "The selected region is currently not accepting new customers"
**Solution**: Always use `swedencentral`, never `westeurope`

### 2. AI Endpoint Authentication
**Problem**: 401 Unauthorized errors
**Solution**: Use Cognitive Services endpoint format:
```
https://jasmin-catering-resource.cognitiveservices.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-01
```

### 3. Email Duplicate Prevention
**Problem**: Emails processed multiple times
**Solution**: 
- Use UNSEEN filter: `(UNSEEN) (TO "ma3u-test@email.de")`
- Mark emails as read after processing: `email_processor.mark_as_read(email_id)`
- Hash-based tracking with `EmailTracker` class

## 🏗️ Architecture Decisions

1. **Azure AI Foundry** for AI capabilities
   - Unified AI platform
   - Project-based organization
   - Uses AI Services infrastructure
   - Direct GPT-4 access via OpenAI API

2. **Container Apps Jobs**
   - Scheduled job execution (cron)
   - Scale-to-zero cost optimization
   - Easy deployment and monitoring

3. **Sweden Central region**
   - West Europe restrictions
   - Good latency
   - Full service availability

4. **Email filtering by recipient**
   - Process only targeted emails
   - Avoid spam processing
   - Clear test scenarios

## 📊 Current Workflow

```
Container Apps Job (*/5 * * * *) → Fetch UNSEEN Emails → AI Assistant Processing → Vector Store RAG → Generate Response → Send Email → Mark as Read
```

## 💡 Key Azure CLI Commands

```bash
# Load environment
source scripts/deployment/utilities/load-env-config.sh

# Deploy to Azure Container Apps
./scripts/deployment/deploy-container-jobs.sh

# Monitor job executions
az containerapp job execution list \
  --name jasmin-email-processor \
  --resource-group logicapp-jasmin-sweden_group \
  --query "[0:5].{Name:name, Status:properties.status, Time:properties.startTime}" -o table

# View latest logs
LATEST=$(az containerapp job execution list --name jasmin-email-processor --resource-group logicapp-jasmin-sweden_group --query "[0].name" -o tsv)
az containerapp job logs show \
  --name jasmin-email-processor \
  --resource-group logicapp-jasmin-sweden_group \
  --job-execution-name $LATEST

# Update job image
az containerapp job update \
  --name jasmin-email-processor \
  --resource-group logicapp-jasmin-sweden_group \
  --image jasmincateringregistry.azurecr.io/jasmin-catering-ai:latest
```

## 🐍 Key Python Operations

```python
# Using Azure AI Assistant
from azure.ai.assistant import AssistantClient
from azure.identity import DefaultAzureCredential

# Initialize assistant
client = AssistantClient(
    endpoint="https://your-ai-service.openai.azure.com/",
    credential=DefaultAzureCredential()
)

# Create thread and run
thread = client.threads.create()
run = client.threads.runs.create(
    thread_id=thread.id,
    assistant_id="asst_UHTUDffJEyLQ6qexElqOopac"
)

# Email processing with duplicate prevention
from core.email_processor import EmailProcessor
from core.email_tracker import EmailTracker

processor = EmailProcessor()
tracker = EmailTracker()

# Fetch only UNSEEN emails
emails = processor.fetch_catering_emails(limit=5)

for email in emails:
    if not tracker.is_processed(email):
        # Process email
        response = ai_assistant.generate_response(email['subject'], email['body'])
        processor.send_response(email['from'], email['subject'], response)
        
        # Mark as processed
        tracker.mark_processed(email)
        processor.mark_as_read(email['id'])  # Critical for duplicate prevention
```

## 📝 Important Context

1. **Client**: Jasmin Catering - Syrian fusion restaurant in Berlin
2. **Language**: All customer communication in German
3. **Pricing**: 35-45€ per person for catering
4. **Business**: Event catering 15-500 guests

## 🚀 Quick Fixes

### If deployment fails:
1. Check region is `swedencentral`
2. Verify `.env` file exists
3. Ensure Azure CLI logged in: `az login`

### If AI processing fails:
1. Verify Cognitive Services endpoint (not AI Foundry)
2. Check API key in `.env`
3. Test endpoint with curl

### If duplicate emails are sent:
1. Verify UNSEEN filter in `fetch_catering_emails()`
2. Check `mark_as_read()` is called after processing
3. Verify email tracker is working: `tracker.is_processed(email)`
4. Check logs: `./scripts/deployment/monitoring/monitor-container-job.sh latest`

## 🎯 Next Steps for New Claude Instance

1. **Read**: Start with this file, then README.md
2. **Check**: Verify `.env` file exists with all variables
3. **Deploy**: Run `scripts/deployment/deploy-container-jobs.sh` if needed
4. **Test**: Send test email to `ma3u-test@email.de`
5. **Monitor**: Use `az containerapp job execution list`

## 📚 Key Files

### Deployment Scripts
- `scripts/deployment/core/deploy-container-jobs.sh` - Main deployment
- `scripts/deployment/core/deploy-full-stack.sh` - Full deployment orchestration
- `scripts/deployment/utilities/load-env-config.sh` - Environment loader
- `scripts/deployment/monitoring/monitor-container-job.sh` - Job monitoring

### Core Implementation
- `core/email_processor.py` - Email handling with UNSEEN filter
- `core/ai_assistant_openai_agent.py` - Azure AI Assistant integration
- `core/email_tracker.py` - Duplicate prevention tracking
- `core/rag_system.py` - Vector Store RAG implementation

### Testing
- `scripts/testing/test-duplicate-prevention.py` - Verify single email processing
- `scripts/testing/send-test-email.py` - Send test emails

Remember: The goal is full automation with zero manual Azure Portal steps!

## 🔍 Implementation Memories

- Remember the latest implementation and deployment in Azure
- Fix implemented to avoid multiple answers to one email
- Always use the unseen filter
- After processing, mark the email as read
- Create and move scripts always to `scripts/deployment/`, never to root
- Always document the purpose of the script (temporary fixes, deployment, or general tasks)

## 🛠️ Architecture Principles

### ⚠️ NEVER Use:
- ❌ Azure Logic Apps (use Container Apps Jobs instead)
- ❌ Manual Azure Portal configuration
- ❌ Hardcoded secrets or credentials

### ✅ ALWAYS Use:
- ✅ Azure Container Apps Jobs for scheduled tasks
- ✅ Azure AI Foundry with Assistants API
- ✅ Azure AI SDK for Python
- ✅ CLI deployment with `az` commands
- ✅ UNSEEN email filter + mark as read
- ✅ Scripts in `scripts/deployment/` subdirectories

## 📖 Official Documentation

- [Azure AI SDK for Python](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents-readme?view=azure-python)
- [Azure Container Apps Jobs](https://learn.microsoft.com/en-us/azure/container-apps/jobs)
- [Azure AI Assistants](https://learn.microsoft.com/en-us/azure/ai-services/openai/assistants-overview)
- [Project GitHub Repository](https://github.com/ibxibx/jasmin-catering-ai-agent)