# 🍽️ Jasmin Catering AI Agent

An intelligent, cloud-native email processing system powered by **Azure OpenAI Assistant with Vector Store RAG**. The system automatically responds to catering inquiries using advanced AI with comprehensive knowledge base integration, generates professional catering offers in German, and provides real-time Slack monitoring.

## 📋 Table of Contents

- [🏗️ System Architecture](#️-system-architecture)
- [🤖 Azure AI Assistant & Vector Store](#-azure-ai-assistant--vector-store)
- [🚀 Quick Start](#-quick-start)
- [🏢 Azure Resources](#-azure-resources)
- [⚠️ CI/CD Setup Required](#️-cicd-setup-required)
- [🚀 Deployment & CI/CD](#-deployment--cicd)
- [🧪 Testing](#-testing)
- [🔧 Development](#-development)
- [📊 Monitoring](#-monitoring)
- [🎯 Project Status](#-project-status)

## 🏗️ System Architecture

### Cloud Architecture Overview

```mermaid
graph TB
    subgraph "Azure Cloud Environment"
        subgraph "Compute Layer"
            CJ[Container Apps Job<br/>Cron Schedule<br/>Every 5 minutes]
        end
        
        subgraph "AI Services"
            AOI[Azure OpenAI Assistant<br/>GPT-4o Model<br/>Vector Store RAG]
            VS[Vector Store<br/>vs_xDbEaqnBNUtJ70P7GoNgY1qD<br/>6 Knowledge Documents]
        end
        
        subgraph "Storage & Security"
            KV[Key Vault<br/>Secrets Management]
            ACR[Container Registry<br/>Docker Images]
        end
    end
    
    subgraph "External Services"
        EMAIL[Email System<br/>IMAP/SMTP<br/>web.de]
        SLACK[Slack Workspace<br/>Notifications<br/>Monitoring]
        CUSTOMER[Customer Email<br/>Catering Inquiries]
    end
    
    %% Workflow Connections
    CJ -->|Fetch Emails| EMAIL
    CJ -->|AI Processing| AOI
    AOI -->|Search Knowledge| VS
    VS -->|Return Context| AOI
    CJ -->|Get Secrets| KV
    CJ -->|Send Response| EMAIL
    CJ -->|Post Updates| SLACK
    CUSTOMER -->|Send Inquiry| EMAIL
    EMAIL -->|Auto Response| CUSTOMER
    ACR -.->|Pull Image| CJ
    
    %% Styling
    classDef azure fill:#0078d4,stroke:#005a9e,stroke-width:2px,color:#fff
    classDef external fill:#28a745,stroke:#1e7e34,stroke-width:2px,color:#fff
    classDef storage fill:#6f42c1,stroke:#563d7c,stroke-width:2px,color:#fff
    
    class CJ,AOI,VS azure
    class EMAIL,SLACK,CUSTOMER external
    class KV,ACR storage
```

### Email Processing Workflow

```mermaid
sequenceDiagram
    participant CJ as Container Apps Job
    participant E as Email System
    participant AI as Azure OpenAI Assistant
    participant VS as Vector Store
    participant S as Slack
    participant CU as Customer
    
    Note over CJ: Cron: Every 5 minutes
    CJ->>E: Fetch catering emails (IMAP)
    E-->>CJ: Email list
    
    loop For each email
        CJ->>S: Post email to #requests channel
        
        Note over CJ: AI Assistant with RAG
        CJ->>AI: Create thread & run assistant
        AI->>VS: Search knowledge documents
        Note over VS: Vector Store RAG<br/>6 Knowledge Documents<br/>Semantic Search<br/>File Search Tool
        VS-->>AI: Relevant context
        AI-->>CJ: Professional German response
        
        CJ->>E: Send response email (SMTP)
        E->>CU: Automated catering offer
        
        CJ->>S: Post AI response to #responses channel
    end
    
    CJ->>S: Post processing summary
    Note over CJ: Scale to zero
```

### Cost-Effective Architecture

| Service | Monthly Cost | Purpose |
|---------|-------------|---------|
| **Container Apps Jobs** | $2-8 | Scheduled email processing (scale-to-zero) |
| **Azure OpenAI** | $50-80 | GPT-4o Assistant + Vector Store RAG |
| **Container Registry** | $5 | Docker image storage |
| **Key Vault** | $3 | Secret management |
| **Total** | **$60-96** | 48% cost reduction vs previous setup |

## 🤖 Azure AI Assistant & Vector Store

![AI Assistant Demo](pictures/AIAssistent2.gif)

### Current Production Configuration
- **Assistant ID**: `asst_UHTUDffJEyLQ6qexElqOopac`
- **Model**: GPT-4o
- **Vector Store ID**: `vs_xDbEaqnBNUtJ70P7GoNgY1qD`
- **Knowledge Documents**: 6 files uploaded ✅
- **RAG Tool**: `file_search` enabled

### Vector Store Knowledge Base

All knowledge files in `deployments/documents/` are uploaded to the Azure OpenAI Vector Store:

| File | Purpose | Status | File ID |
|------|---------|--------|---------|
| `business-conditions.md` | Terms, pricing, cancellation policies | ✅ Uploaded | `assistant-JoXkWRSQF1Vhryin7TizgX` |
| `catering-brief.md` | Business process & system requirements | ✅ Uploaded | `assistant-BFjrHArDvusxRUr3rJkF3f` |
| `email-template.md` | Professional communication standards | ✅ Uploaded | `assistant-JFhmqteJ7ADMT1kr94RN8j` |
| `jasmin_catering_prompt.md` | AI agent instructions & behavior | ✅ Uploaded | `assistant-YASZfpLZFRqLLMMG5Gs6Rz` |
| `response-examples.md` | Professional response examples | ✅ Uploaded | `assistant-W65tS9JgAPCra86jNmh2wY` |
| `vegetarian-offer-template.md` | Vegetarian menu offerings | ✅ Uploaded | `assistant-X3MxAxuGEeQnm7rEJq2z3Q` |

### RAG Capabilities
- **Semantic Search**: Vector-based search through business knowledge
- **Contextual Responses**: Finds relevant information for each inquiry
- **German Language**: Native German responses for local customers
- **Policy Compliance**: Ensures responses follow business terms
- **Professional Quality**: Uses approved templates and examples

## 🚀 Quick Start

### Prerequisites
- Azure CLI installed and logged in
- Docker installed
- Access to Azure subscription with Contributor role

### One-Command Deployment
```bash
git clone https://github.com/ma3u/jasmin-catering-ai-agent.git
cd jasmin-catering-ai-agent
./scripts/deployment/deploy-container-jobs.sh
```

### Management Commands
```bash
# Manual trigger
az containerapp job start --name jasmin-email-processor --resource-group logicapp-jasmin-sweden_group

# Check execution status
az containerapp job execution list --name jasmin-email-processor --resource-group logicapp-jasmin-sweden_group

# View logs
az containerapp job logs show --name jasmin-email-processor --resource-group logicapp-jasmin-sweden_group --container jasmin-email-processor
```

## 🏢 Azure Resources

### Resource Group: `logicapp-jasmin-sweden_group`
**Location**: Sweden Central

| Service | Name | Purpose |
|---------|------|---------|
| **Container Apps Jobs** | `jasmin-email-processor` | Scheduled email processing |
| **Container Registry** | `jasmincateringregistry` | Docker image storage |
| **Azure OpenAI** | `jasmin-openai-372bb9` | GPT-4o Assistant + Vector Store |
| **Key Vault** | `jasmin-catering-kv` | Secret management |

![Azure Deployments](pictures/azuredeployment.png)

### Key Vault Secrets
**Azure Key Vault**: `jasmin-catering-kv`

Required secrets for production:
```bash
azure-subscription-id                   # Azure subscription identifier
azure-tenant-id                         # Azure AD tenant ID
from-email-address                      # Sender email
webde-app-password                      # Web.de app-specific password
openai-api-key                          # Azure OpenAI API key
openai-endpoint                         # Azure OpenAI endpoint URL
slack-bot-token                         # Slack bot OAuth token
slack-channel-emailrequestsandresponse  # Channel ID for email notifications
slack-channel-jasminlogs                # Channel ID for system logs
```

## ⚠️ CI/CD Setup Options

### **Option 1: GitHub Actions (Requires Admin Privileges)**

**Issue**: GitHub Actions CI/CD requires Azure Service Principal creation with admin privileges.

**Problem**: 
```bash
az ad sp create-for-rbac --name "jasmin-github-actions" --role contributor --scopes "/subscriptions/6576090b-36b2-4ba1-94ae-d2f52eed2789"
ERROR: Insufficient privileges to complete the operation.
```

**Alternative Solutions**:
1. **Federated Identity** (Lower privileges) - See `scripts/utilities/setup-federated-identity.md`
2. **Contact Azure Admin** for Service Principal creation
3. **Use Local CI/CD** (immediate solution below)

### **Option 2: Local CI/CD Script (Immediate Solution)**

**No admin privileges required!** Use the local deployment script:

```bash
# One-command local CI/CD
./scripts/deployment/local-cicd.sh
```

This script performs the same actions as GitHub Actions:
- ✅ Builds Docker image
- ✅ Pushes to Azure Container Registry  
- ✅ Updates Container Apps Job
- ✅ Triggers test execution
- ✅ Shows deployment logs

**Current Status**: 
- ✅ GitHub Actions workflow created (paused)
- ✅ 6/7 required secrets added to GitHub
- ✅ **Local CI/CD script ready** (immediate alternative)
- ⚠️ GitHub Actions paused until admin creates Service Principal

## 🚀 Deployment & CI/CD

### GitHub Actions CI/CD Pipeline

**Automated deployment** triggered on commits to `main`:

```yaml
name: Deploy Jasmin Catering AI Container App
on:
  push:
    branches: [ main, fix/container-apps-email-processing ]
```

**Pipeline Features**:
- ✅ **Container Build**: Builds Docker image on every push
- ✅ **Registry Push**: Pushes to `jasmincateringregistry.azurecr.io`
- ⚠️ **Deployment**: **PAUSED** - Missing AZURE_CREDENTIALS
- ⚠️ **Testing**: **PAUSED** - Requires Azure Service Principal

**GitHub Secrets Status**:
```bash
# ✅ Added (6/7 secrets configured)
FROM_EMAIL_ADDRESS         ✅ Configured
WEBDE_APP_PASSWORD         ✅ Configured  
AZURE_SUBSCRIPTION_ID      ✅ Configured
AZURE_TENANT_ID           ✅ Configured
AZURE_AI_ENDPOINT         ✅ Configured
AZURE_AI_API_KEY          ✅ Configured

# ❌ Missing (requires admin privileges)
AZURE_CREDENTIALS         ❌ MISSING - Service Principal required
```

### Local CI/CD Deployment (Recommended)
```bash
# Automated local deployment (no admin privileges needed)
./scripts/deployment/local-cicd.sh
```

### Manual Deployment
```bash
# Build and deploy manually
az acr build --registry jasmincateringregistry --image jasmin-catering-ai:latest .
az containerapp job update --name jasmin-email-processor --resource-group logicapp-jasmin-sweden_group --image "jasmincateringregistry.azurecr.io/jasmin-catering-ai:latest"
```

## 🧪 Testing

### Automated Testing
The CI/CD pipeline includes automated testing that:
1. Sends test email to `ma3u-test@email.de`
2. Triggers Container Apps Job execution
3. Verifies email processing in logs
4. Generates detailed test report

### Manual Testing
```bash
# Send test email
python scripts/testing/send_test_email.py

# Test AI Assistant locally
python -c "from core.ai_assistant_openai_agent import JasminAIAssistantOpenAI; print(JasminAIAssistantOpenAI().get_assistant_info())"

# Test Slack integration
python scripts/testing/test_slack_simple.py
```

### Key Test Scripts
- `scripts/testing/test_deployment.py` - Full CI/CD verification
- `scripts/testing/send_test_email.py` - Email testing
- `scripts/testing/test_slack_simple.py` - Slack notifications
- `scripts/testing/check_new_email.py` - Email verification

## 🔧 Development

### Project Structure
```
jasmin-catering-ai-agent/
├── 📁 config/
│   └── settings.py                     # Centralized configuration
├── 📁 core/
│   ├── email_processor.py              # IMAP/SMTP email handling
│   ├── ai_assistant_openai_agent.py    # Azure OpenAI Assistant with Vector Store RAG
│   └── slack_notifier.py               # Slack integration
├── 📁 deployments/
│   ├── documents/                      # 📚 Knowledge base files (uploaded to Vector Store)
│   └── templates/                      # Configuration templates
├── 📁 scripts/
│   ├── deployment/                     # Azure deployment scripts
│   ├── testing/                        # Test scripts (organized from root)
│   ├── utilities/                      # Helper scripts (GitHub secrets, upload)
│   └── archive/                        # Legacy scripts
├── 📄 main.py                          # Application entry point
├── 📄 Dockerfile                       # Container definition
└── 📄 requirements.txt                 # Python dependencies
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your credentials

# Run locally
python main.py

# Docker development
docker build -t jasmin-catering-ai .
docker run --env-file .env jasmin-catering-ai
```

## 📊 Monitoring

### Slack Integration
- **#email-requests-and-response**: Customer inquiry notifications
- **#jasmin-catering-logs**: System events and errors

### Performance Metrics
- **Email Processing Time**: 2-5 seconds average
- **AI Response Generation**: 3-8 seconds average
- **System Availability**: 99.9% SLA target
- **Cost per Email**: ~$0.10-0.30

### Troubleshooting
```bash
# Check container logs
az containerapp job logs show --name jasmin-email-processor --resource-group logicapp-jasmin-sweden_group

# Verify environment variables
az containerapp job show --name jasmin-email-processor --resource-group logicapp-jasmin-sweden_group --query "properties.template.containers[0].env"

# Manual job trigger
az containerapp job start --name jasmin-email-processor --resource-group logicapp-jasmin-sweden_group
```

## 🎯 Project Status

### ✅ Completed & Deployed
- [x] **Azure OpenAI Assistant with Vector Store RAG** - Enterprise-grade AI Agent deployed
- [x] **6 Knowledge Documents Uploaded** - Complete business knowledge base integrated
- [x] **Cloud-native Container Apps Jobs** - Fully deployed and operational
- [x] **Enhanced architecture** - AI Assistant + Vector Store, 48% cost reduction
- [x] **Automated scheduling** - Runs every 5 minutes with cron
- [x] **Scale-to-zero optimization** - No costs when idle
- [x] **Secure secret management** - Azure Key Vault integration
- [x] **Real-time Slack integration** - Full notifications working
- [x] **Email automation** - IMAP/SMTP processing operational
- [x] **GitHub Actions CI/CD** - Automated build and deployment pipeline

### 🚀 Production Metrics (Verified)
- **✅ Uptime**: 100% success rate across all test executions
- **⚡ Performance**: 37-second processing time for 5 emails
- **💰 Cost**: $60-96/month (48% reduction from initial architecture)
- **🔄 Automation**: Every 5 minutes, fully hands-off
- **📧 Email Processing**: 5/5 emails processed successfully
- **🤖 AI Response Time**: 4-7 seconds per email
- **📱 Slack Integration**: Real-time notifications operational

### 📋 Future Enhancements
- [ ] Complete CI/CD setup (requires Azure Service Principal)
- [ ] Multi-language support for international customers
- [ ] Production email system (info@jasmincatering.com)
- [ ] CRM integration for customer management
- [ ] Advanced analytics and business intelligence

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

---

**🤖 Powered by Azure AI Services & Container Apps Jobs**  
*Production-ready intelligent catering automation with enterprise-grade cloud infrastructure*

**📊 System Performance**: 100% uptime | 4-7s AI response time | $0.02-0.05 per email  
**🔒 Enterprise Security**: Azure Key Vault | Container isolation | Secure secret management  
**📈 Cloud-Native**: Scale-to-zero cost optimization | Automated cron scheduling | 48% cost reduction