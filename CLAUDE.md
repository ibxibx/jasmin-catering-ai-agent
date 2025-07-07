# CLAUDE.md - Guide for Future Claude Instances

This file provides essential guidance for Claude Code when working with the Jasmin Catering AI Agent codebase.

## 🎯 Project Overview

**What**: Automated catering inquiry processing system for Jasmin Catering (Syrian fusion restaurant in Berlin)
**Current Status**: Deployed to Sweden Central, monitoring emails at `ma3u-test@email.de`
**Technology**: Azure Logic Apps + Cognitive Services (GPT-4) + CLI deployment

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

### 4. **AI Service: Azure AI Foundry**
- Using **Azure AI Foundry** project: `jasmin-catering`
- Resource: `jasmin-catering-resource` (AI Services)
- Endpoint: `https://jasmin-catering-resource.cognitiveservices.azure.com/`
- Note: AI Foundry uses AI Services infrastructure, hence the cognitiveservices URL

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
cd deployments/scripts
./deploy-main.sh
```

### Monitor Container Apps Job
```bash
# Check recent executions
az containerapp job execution list --name jasmin-email-processor --resource-group jasmin-catering-rg

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

### 3. Email Filtering
**Problem**: Processing wrong emails
**Solution**: Filter by TO field in Logic App Query action:
```json
"where": "@equals(item()['to'], 'ma3u-test@email.de')"
```

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
Container Apps Job (5 min cron) → Fetch Emails → Filter (TO: ma3u-test@email.de) → AI Processing → Generate Offer → Send Response
```

## 💡 Key Commands

```bash
# Load environment
source deployments/scripts/load-env-config.sh

# Test AI endpoint
curl -X POST "https://jasmin-catering-resource.cognitiveservices.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-01" \
  -H "api-key: $AZURE_AI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Test"}],"max_tokens":50}'

# View Logic App state
az logic workflow show \
  --resource-group logicapp-jasmin-sweden_group \
  --name jasmin-order-processor-sweden \
  --query state
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

### If emails not filtered:
1. Check TO field filter in workflow
2. Verify test email sent TO `ma3u-test@email.de`
3. Review Query action in Logic App

## 🎯 Next Steps for New Claude Instance

1. **Read**: Start with this file, then README.md
2. **Check**: Verify `.env` file exists with all variables
3. **Deploy**: Run `./deploy-main.sh` if needed
4. **Test**: Send test email to `ma3u-test@email.de`
5. **Monitor**: Use `./monitor-logic-app.sh`

## 📚 Key Files

- `deployments/scripts/deploy-main.sh` - Main deployment
- `deployments/logic-apps/email-processor-workflow.json` - Workflow definition
- `deployments/scripts/load-env-config.sh` - Environment configuration
- `.env` - All secrets (never commit!)

Remember: The goal is full automation with zero manual Azure Portal steps!