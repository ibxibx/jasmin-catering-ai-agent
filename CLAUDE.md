# CLAUDE.md - Guide for Future Claude Instances

This file provides essential guidance for Claude Code when working with the Jasmin Catering AI Agent codebase.

## 🎯 Project Overview

**What**: Automated catering inquiry processing system for Jasmin Catering (Syrian fusion restaurant in Berlin)
**Current Status**: Deployed to Sweden Central, monitoring emails at `ma3u-test@email.de`
**Technology**: Azure Container Apps + Azure AI Foundry Assistants + CLI deployment

## 🚀 Quick Start Commands

```bash
# First time setup
source scripts/deployment/utilities/load-env-config.sh
az login
./scripts/deployment/deploy-container-jobs.sh

# Daily operations
./scripts/deployment/monitoring/monitor-container-job.sh stats  # Check health
python scripts/testing/send-test-email.py                      # Test system
./scripts/deployment/monitoring/monitor-container-job.sh latest # View logs

# Common fixes
az containerapp job start --name jasmin-email-processor --resource-group logicapp-jasmin-sweden_group  # Restart job
```

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

## 💡 Common Command-Line Operations

### 🔧 Local Development Commands

```bash
# Environment Setup
source scripts/deployment/utilities/load-env-config.sh  # Load environment variables
python -m venv venv                                    # Create virtual environment
source venv/bin/activate                               # Activate virtual environment
pip install -r requirements.txt                        # Install dependencies

# Testing
python scripts/testing/test-duplicate-prevention.py    # Test email duplicate prevention
python scripts/testing/send-test-email.py             # Send test email to ma3u-test@email.de
python main.py                                        # Run application locally

# Git Operations
git status                                            # Check changes
git add -A                                           # Stage all changes
git commit -m "feat: description"                    # Commit with conventional message
git push origin main                                 # Push to origin
gh pr create --repo ibxibx/jasmin-catering-ai-agent # Create PR to upstream

# Monitoring
./scripts/deployment/monitoring/monitor-container-job.sh list    # List executions
./scripts/deployment/monitoring/monitor-container-job.sh latest  # View latest logs
./scripts/deployment/monitoring/monitor-container-job.sh stats   # Show statistics
```

### ☁️ Azure CLI Commands

```bash
# Authentication & Setup
az login                                              # Login to Azure
az account set --subscription $AZURE_SUBSCRIPTION_ID  # Set subscription
az group list --query "[?contains(name, 'jasmin')]" -o table  # Find resource groups

# Container Apps Job Management
az containerapp job list \
  --resource-group logicapp-jasmin-sweden_group \
  --query "[].name" -o tsv                           # List all jobs

az containerapp job show \
  --name jasmin-email-processor \
  --resource-group logicapp-jasmin-sweden_group \
  --query "{status:properties.runningStatus, schedule:properties.configuration.scheduleTriggerConfig.cronExpression}" \
  -o json                                            # Show job details

az containerapp job execution list \
  --name jasmin-email-processor \
  --resource-group logicapp-jasmin-sweden_group \
  --query "[0:10].{Name:name, Status:properties.status, Time:properties.startTime}" \
  -o table                                           # List recent executions

# Manual Job Execution
az containerapp job start \
  --name jasmin-email-processor \
  --resource-group logicapp-jasmin-sweden_group      # Manually trigger job

# View Logs
LATEST=$(az containerapp job execution list \
  --name jasmin-email-processor \
  --resource-group logicapp-jasmin-sweden_group \
  --query "[0].name" -o tsv)

az containerapp logs show \
  --name jasmin-email-processor \
  --resource-group logicapp-jasmin-sweden_group \
  --type system                                      # System logs

# Container Registry
az acr repository list \
  --name jasmincateringregistry \
  -o table                                           # List repositories

az acr repository show-tags \
  --name jasmincateringregistry \
  --repository jasmin-catering-ai \
  --orderby time_desc \
  --top 5 -o tsv                                     # Show recent image tags

# Key Vault Secrets
az keyvault secret list \
  --vault-name jasmin-catering-kv \
  --query "[].name" -o tsv                           # List all secrets

az keyvault secret show \
  --vault-name jasmin-catering-kv \
  --name openai-api-key \
  --query "value" -o tsv                             # Get secret value

# Deployment
./scripts/deployment/deploy-container-jobs.sh        # Full deployment
./scripts/deployment/core/deploy-full-stack.sh --dry-run  # Dry run deployment

# Update Container Image
az containerapp job update \
  --name jasmin-email-processor \
  --resource-group logicapp-jasmin-sweden_group \
  --image jasmincateringregistry.azurecr.io/jasmin-catering-ai:latest

# Environment Variables
az containerapp job show \
  --name jasmin-email-processor \
  --resource-group logicapp-jasmin-sweden_group \
  --query "properties.template.containers[0].env[].name" \
  -o tsv                                             # List env variables
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

## 🚀 Quick Fixes & Troubleshooting

### Common Operations by Scenario

#### 🔍 Check System Health
```bash
# Quick health check
./scripts/deployment/monitoring/monitor-container-job.sh stats
az containerapp job show --name jasmin-email-processor --resource-group logicapp-jasmin-sweden_group --query "properties.runningStatus"
```

#### 🐛 Debug Failed Execution
```bash
# Get failed execution name
FAILED=$(az containerapp job execution list --name jasmin-email-processor --resource-group logicapp-jasmin-sweden_group --query "[?properties.status=='Failed'][0].name" -o tsv)

# View logs
az containerapp logs show --name jasmin-email-processor --resource-group logicapp-jasmin-sweden_group --type system

# Check container logs
az containerapp logs show --name jasmin-email-processor --resource-group logicapp-jasmin-sweden_group --container jasmin-email-processor
```

#### 📧 Test Email Processing
```bash
# Send test email
python scripts/testing/send-test-email.py

# Wait 5 minutes, then check
sleep 300 && ./scripts/deployment/monitoring/monitor-container-job.sh latest | grep -E "(Processing|UNSEEN|Skipping)"
```

#### 🔄 Update and Redeploy
```bash
# Make code changes, then:
git add -A && git commit -m "fix: description"
./scripts/deployment/deploy-container-jobs.sh
# Monitor deployment
watch -n 10 'az containerapp job show --name jasmin-email-processor --resource-group logicapp-jasmin-sweden_group --query "properties.provisioningState"'
```

#### 🔑 Update Secrets
```bash
# Update in Key Vault
az keyvault secret set --vault-name jasmin-catering-kv --name "secret-name" --value "new-value"

# Restart job to pick up new secrets
az containerapp job stop --name jasmin-email-processor --resource-group logicapp-jasmin-sweden_group
az containerapp job start --name jasmin-email-processor --resource-group logicapp-jasmin-sweden_group
```

### If deployment fails:
1. Check region is `swedencentral`
2. Verify `.env` file exists
3. Ensure Azure CLI logged in: `az login`
4. Check ACR access: `az acr login --name jasmincateringregistry`

### If AI processing fails:
1. Verify AI endpoint in environment
2. Check API key: `az keyvault secret show --vault-name jasmin-catering-kv --name openai-api-key`
3. Test Assistant: `python -c "from core.ai_assistant_openai_agent import JasminAIAssistantOpenAI; ai = JasminAIAssistantOpenAI(); print(ai.assistant_id)"`

### If duplicate emails are sent:
1. Verify UNSEEN filter: `grep -n "UNSEEN" core/email_processor.py`
2. Check mark_as_read calls: `grep -n "mark_as_read" main.py`
3. Verify email tracker: `ls -la /tmp/processed_emails.json`
4. Check logs: `./scripts/deployment/monitoring/monitor-container-job.sh latest | grep -E "(Already processed|Skipping)"`

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
- **New Memory**: Key and common Azure and local CLI operations added for easier reference and quick access to critical commands

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