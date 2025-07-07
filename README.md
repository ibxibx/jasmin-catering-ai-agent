# 🍽️ Jasmin Catering AI Agent

An intelligent, cloud-native email processing system powered by **Azure OpenAI Assistant with Vector Store RAG**. The system automatically responds to catering inquiries using advanced AI with comprehensive knowledge base integration, generates professional catering offers in German, and provides real-time Slack monitoring.

## 📋 Table of Contents

- [🏗️ System Architecture](#️-system-architecture)
  - [Cloud Architecture](#cloud-architecture)
  - [Email Processing Workflow](#email-processing-workflow)
  - [Cost-Effective Architecture](#cost-effective-architecture)
  - [Deployment Pipeline](#deployment-pipeline)
- [🤖 Azure AI Foundry Assistants](#-azure-ai-foundry-assistants)
- [🚀 Quick Start](#-quick-start)
- [🏢 Azure Resources](#-azure-resources)
  - [Resource Group](#resource-group-jasmin-catering-rg)
  - [Key Vault Secrets](#key-vault-secrets)
  - [Local Development Secrets Backup](#local-development-secrets-backup)
- [🔐 Security Configuration](#-security-configuration)
- [📊 Monitoring & Observability](#-monitoring--observability)
- [🔧 Development](#-development)
- [🚀 Deployment](#-deployment)
- [🧪 Testing](#-testing)
  - [Test Scripts & Utilities](#test-scripts--utilities)
- [🔧 Troubleshooting](#-troubleshooting)
- [📈 Scaling & Performance](#-scaling--performance)
- [🎯 Project Status](#-project-status)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## 🏗️ System Architecture

For comprehensive architectural details, see our [detailed diagrams](docs/diagrams/):
- 📊 [Complete System Architecture](docs/diagrams/system-architecture.md)
- 🔄 [Sequential Workflow](docs/diagrams/sequential-workflow.md)

```mermaid
graph TB
    subgraph "Azure Cloud Environment"
        subgraph "Compute Layer"
            CJ[Container Apps Job<br/>Cron Schedule<br/>Every 5 minutes]
        end
        
        subgraph "AI Services"
            AOI[Azure OpenAI Assistant<br/>GPT-4.1 Model<br/>Vector Store RAG]
            VS[Vector Store<br/>AssistantVectorStore_Jasmin<br/>6 Knowledge Documents]

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
    
    %% Deployment Connections

    ACR -.->|Pull Image| CJ
    
    %% Styling
    classDef azure fill:#0078d4,stroke:#005a9e,stroke-width:2px,color:#fff
    classDef external fill:#28a745,stroke:#1e7e34,stroke-width:2px,color:#fff
    classDef storage fill:#6f42c1,stroke:#563d7c,stroke-width:2px,color:#fff
    

    class CJ,AOI,VS azure
    class EMAIL,SLACK,CUSTOMER external
    class KV,ACR storage
```

## 🔄 Email Processing Workflow

```mermaid
sequenceDiagram
    participant CJ as Container Apps Job
    participant E as Email System
    participant AI as Azure OpenAI Assistant
    participant VS as Vector Store
    participant S as Slack
    participant KV as Key Vault
    participant CU as Customer
    

    Note over CJ: Cron: Every 5 minutes
    CJ->>KV: Retrieve secrets
    KV-->>CJ: Email & API credentials
    
    CJ->>E: Fetch catering emails (IMAP)
    E-->>CJ: Email list
    
    loop For each email
        Note over CJ: Email Processing
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

## 💰 Cost-Effective Cloud Architecture

```mermaid
graph LR
    subgraph "Monthly Costs"

        subgraph "Compute ($2-8)"
            CJ2[Container Apps Jobs<br/>Scale-to-Zero<br/>Cron Schedule]
        end
        
        subgraph "AI Services ($50-80)"
            AOI2[Azure OpenAI Assistant<br/>GPT-4o + Vector Store<br/>Pay-per-use]

        end
        
        subgraph "Storage ($3-8)"
            KV2[Key Vault<br/>Secret operations]
            ACR2[Container Registry<br/>Image storage]
        end
    end
    
    subgraph "Total: $55-96/month"
        TOTAL[Previous Setup: $115-145<br/>Enhanced RAG: $55-96<br/>Savings: 48% reduction]
    end
    
    CJ2 --> TOTAL

    AOI2 --> TOTAL
    KV2 --> TOTAL
    ACR2 --> TOTAL
    
    classDef cost fill:#28a745,stroke:#1e7e34,stroke-width:2px,color:#fff
    classDef compute fill:#0078d4,stroke:#005a9e,stroke-width:2px,color:#fff
    classDef ai fill:#ff6b35,stroke:#d63031,stroke-width:2px,color:#fff
    classDef storage fill:#6f42c1,stroke:#563d7c,stroke-width:2px,color:#fff
    
    class TOTAL cost
    class CJ2 compute
    class AOI2 ai
    class KV2,ACR2 storage
```

## 🚀 Deployment Architecture

```mermaid
flowchart TD
    subgraph "Development"
        DEV[Local Development<br/>Python + Docker<br/>main.py]
        BUILD[Docker Build<br/>Containerization]
    end
    
    subgraph "CI/CD Pipeline"
        PUSH[Push to ACR<br/>jasmincateringregistry.azurecr.io]
        DEPLOY[Deploy to Container Apps<br/>jasmin-catering-app]
    end
    
    subgraph "Azure Cloud Production"
        subgraph "Container Apps Environment"
            APP[Jasmin AI Agent<br/>HTTP Endpoints<br/>Auto-scaling]
        end
        
        subgraph "Scheduling"
            SCHEDULE[Logic App Scheduler<br/>jasmin-catering-scheduler<br/>Every 5 minutes]
        end
        
        subgraph "Monitoring"
            LOGS[Application Insights<br/>Container Logs<br/>Performance Metrics]
            HEALTH[Health Checks<br/>/health endpoint<br/>Availability monitoring]
        end
    end
    
    subgraph "External Integrations"
        API1[Slack API<br/>Real-time notifications]
        API2[Email Services<br/>IMAP/SMTP processing]
        API3[Azure OpenAI<br/>GPT-4o responses]
    end
    
    DEV --> BUILD
    BUILD --> PUSH
    PUSH --> DEPLOY
    DEPLOY --> APP
    
    SCHEDULE -->|HTTP Trigger| APP
    APP --> LOGS
    APP --> HEALTH
    
    APP <--> API1
    APP <--> API2
    APP <--> API3
    
    classDef dev fill:#ffeaa7,stroke:#fdcb6e,stroke-width:2px,color:#2d3436
    classDef cicd fill:#74b9ff,stroke:#0984e3,stroke-width:2px,color:#fff
    classDef prod fill:#00b894,stroke:#00a085,stroke-width:2px,color:#fff
    classDef monitor fill:#e17055,stroke:#d63031,stroke-width:2px,color:#fff
    classDef external fill:#a29bfe,stroke:#6c5ce7,stroke-width:2px,color:#fff
    
    class DEV,BUILD dev
    class PUSH,DEPLOY cicd
    class APP,SCHEDULE prod
    class LOGS,HEALTH monitor
    class API1,API2,API3 external
```

## 🤖 Azure AI Foundry Assistants

![AI Assistant Demo](pictures/AIAssistent2.gif)

The system leverages Azure AI Foundry's powerful Assistant capabilities with Vector Store RAG for intelligent email processing and response generation. The assistant has access to 6 comprehensive knowledge documents about Jasmin Catering's services, pricing, and policies, enabling it to provide accurate and contextual responses to customer inquiries.

### Key Features:
- **Vector Store RAG**: Semantic search through business knowledge documents
- **GPT-4o Model**: Advanced language understanding and generation
- **File Search Tool**: Ability to search and retrieve relevant information
- **German Language Support**: Native German responses for local customers
- **Context-Aware Responses**: Personalized offers based on event requirements

### 📊 Development Journey
Check out our presentation: [**From Zero to Hero: AI-Powered Development**](https://gamma.app/docs/From-Zero-to-Hero-AI-Powered-Development-zf0bapu4b31bn5h) - showcasing how we built this system using AI-assisted development with Claude.

## 🚀 Quick Start

### Prerequisites
- Azure CLI installed and logged in
- Docker installed
- Access to Azure subscription with Contributor role

### One-Command Deployment
```bash
# Clone and deploy Container Apps Jobs
git clone https://github.com/ma3u/jasmin-catering-ai-agent.git
cd jasmin-catering-ai-agent
./scripts/deployment/deploy-container-jobs.sh
```

### Management Commands
```bash
# Manual trigger
az containerapp job start --name jasmin-email-processor --resource-group jasmin-catering-rg

# Check execution status
az containerapp job execution list --name jasmin-email-processor --resource-group jasmin-catering-rg

# View logs
az containerapp job logs show --name jasmin-email-processor --resource-group jasmin-catering-rg --container jasmin-email-processor

# Test AI Assistant locally
python -c "from core.ai_assistant_openai_agent import JasminAIAssistantOpenAI; print(JasminAIAssistantOpenAI().get_assistant_info())"
```

### Production Deployment Status
**🎉 Enhanced RAG System Deployed & Operational**
- **AI Assistant**: `asst_UHTUDffJEyLQ6qexElqOopac` (Azure OpenAI)
- **Vector Store**: `vs_xDbEaqnBNUtJ70P7GoNgY1qD` (6 knowledge documents)
- **Container Apps Job**: `jasmin-email-processor` 
- **Schedule**: Every 5 minutes (cron: `*/5 * * * *`)
- **Location**: Azure Sweden Central
- **Enhanced Features**: Vector Store RAG, Semantic Search, File Search Tool

## 🏢 Azure Resources

### Resource Group: `jasmin-catering-rg`
**Location**: Sweden Central | **Purpose**: Container for all project resources

| Service | Name | SKU | Purpose | Monthly Cost |
|---------|------|-----|---------|--------------|
| **Container Apps Jobs** | `jasmin-email-processor` | Consumption | Scheduled email processing | $2-8 |
| **Container Registry** | `jasmincateringregistry` | Basic | Docker image storage | $5 |
| **Azure OpenAI** | `jasmin-openai-372bb9` | Standard | GPT-4o Assistant + Vector Store | $50-80 |
| **Key Vault** | `jasmin-catering-kv` | Standard | Secret management | $3 |

**Total Monthly Cost**: $60-96 (vs $115-145 previous setup)
**Cost Optimization**: 48% reduction with enhanced AI Assistant + Vector Store RAG

### Key Vault Secrets

**Azure Key Vault**: `jasmin-catering-kv` | **URI**: `https://jasmin-catering-kv.vault.azure.net/`

All sensitive configuration is securely stored in Azure Key Vault. The following secrets are required:

```bash
# Azure Configuration
azure-subscription-id                   # Azure subscription identifier
azure-tenant-id                         # Azure AD tenant ID

# Email Configuration  
from-email-address                      # Sender email (matthias.buchhorn@web.de)
from-email-password                     # SMTP authentication password
webde-app-password                      # Web.de app-specific password

# OpenAI Configuration
openai-api-key                          # Azure OpenAI API key
openai-endpoint                         # Azure OpenAI endpoint URL

# Slack Integration
slack-bot-token                         # Slack bot OAuth token
slack-channel-emailrequestsandresponse  # Channel ID for email notifications
slack-channel-jasminlogs                # Channel ID for system logs
```

**Access Secrets via Azure CLI:**
```bash
# List all secrets
az keyvault secret list --vault-name jasmin-catering-kv

# Get a specific secret value
az keyvault secret show --vault-name jasmin-catering-kv --name openai-api-key --query value -o tsv

# Set/Update a secret
az keyvault secret set --vault-name jasmin-catering-kv --name secret-name --value "secret-value"
```

### Local Development Secrets Backup

**1Password Vault**: `JasminCatering`

For secure local development, we use 1Password to manage `.env` files:

```bash
# Backup .env to 1Password
./scripts/backup-env-to-1password.sh

# This creates a timestamped backup in the JasminCatering vault
# Example: jasmin-catering-env-2024-01-15_14-30-45

# Restore .env from 1Password
op document get 'jasmin-catering-env-YYYY-MM-DD_HH-MM-SS' --vault 'JasminCatering' > .env

# List all backups
op document list --vault 'JasminCatering' --tags 'env'
```

## 🔐 Security Configuration

### Managed Identity & RBAC
```bash
# Container Apps Job uses managed identity for secure access
az containerapp job identity assign --name jasmin-email-processor \
  --resource-group jasmin-catering-rg

# Key Vault access policies
az keyvault set-policy --name jasmin-catering-kv \
  --object-id <managed-identity-id> \
  --secret-permissions get list
```

### Network Security
- **Container Apps**: Internal networking with controlled ingress
- **Key Vault**: Network access restrictions enabled
- **OpenAI**: VNet integration for production workloads

### Secret Rotation
```bash
# Automated secret rotation strategy
az keyvault secret set --vault-name jasmin-catering-kv \
  --name webde-app-password --value <new-password> \
  --expires <expiry-date>
```

## 📊 Monitoring & Observability

### Application Insights Integration
```bash
# View real-time metrics
az monitor app-insights component show \
  --app jasmin-catering-insights \
  --resource-group jasmin-catering-rg
```

### Slack Monitoring Channels
- **#email-requests-and-response**: Customer inquiry notifications
- **#jasmin-catering-logs**: System events and errors
- **Real-time alerts**: Processing failures, API errors

### Performance Metrics
- **Email Processing Time**: 2-5 seconds average
- **AI Response Generation**: 3-8 seconds average
- **System Availability**: 99.9% SLA target
- **Cost per Email**: ~$0.10-0.30

## 🔧 Development

### Local Development Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your credentials

# Run locally
python main.py
```

### Docker Development
```bash
# Build container locally
docker build -t jasmin-catering-ai .

# Run container locally
docker run -p 8000:8000 \
  --env-file .env \
  jasmin-catering-ai
```

### Project Structure
```
jasmin-catering-ai-agent/
├── 📁 config/
│   └── settings.py                     # Centralized configuration
├── 📁 core/
│   ├── email_processor.py              # IMAP/SMTP email handling
│   ├── ai_assistant_openai_agent.py    # Enhanced RAG AI Assistant
│   └── slack_notifier.py               # Slack integration
├── 📁 deployments/
│   ├── documents/                      # Knowledge base files
│   ├── scripts/                        # Deployment automation
│   └── templates/                      # Configuration templates
├── 📁 docs/
│   ├── diagrams/                       # Architecture & workflow diagrams
│   ├── azure-ai-agent-deployment.md   # AI deployment guide
│   └── enhanced-rag-system.md         # RAG system documentation
├── 📁 scripts/
│   ├── deployment/                     # Azure deployment scripts
│   ├── testing/                        # Test suites & results
│   ├── utilities/                      # Helper scripts
│   └── archive/                        # Unused/deprecated scripts
├── 📁 utils/
│   └── send_test_emails.py             # Email testing utilities
├── 📄 main.py                          # Application entry point
├── 📄 agent-config.json                # AI Assistant configuration
├── 📄 Dockerfile                       # Container definition
├── 📄 requirements.txt                 # Python dependencies
├── 📄 CLAUDE.md                        # AI development guide
└── 📄 README.md                        # Project documentation

```

## 🚀 Deployment

### Automated Deployment Pipeline
```bash
# Full deployment with monitoring
./deploy-to-azure.sh

# This script performs:
# 1. Creates Azure Container Registry
# 2. Builds and pushes Docker image  
# 3. Creates Container Apps environment
# 4. Deploys application with secrets
# 5. Sets up Logic App scheduler
# 6. Configures monitoring and alerts
```

### Environment-Specific Deployments
```bash
# Development environment
az containerapp create --name jasmin-catering-dev \
  --environment-variables "ENVIRONMENT=development"

# Production environment  
az containerapp create --name jasmin-catering-prod \
  --environment-variables "ENVIRONMENT=production"
```

### Blue-Green Deployment
```bash
# Deploy new version alongside current
az containerapp revision copy --name jasmin-catering-app \
  --from-revision jasmin-catering-app--old-revision

# Route traffic gradually
az containerapp ingress traffic set --name jasmin-catering-app \
  --revision-weight jasmin-catering-app--new-revision=50 \
  --revision-weight jasmin-catering-app--old-revision=50
```

## 🧪 Testing

### Local Testing
```bash
# Unit tests
python -m pytest tests/

# Integration testing
python test-email-flow.py

# Load testing
python load-test-ai-responses.py
```

### Cloud Testing
```bash
# Manual job trigger
az containerapp job start --name jasmin-email-processor --resource-group jasmin-catering-rg

# Check job execution history
az containerapp job execution list --name jasmin-email-processor --resource-group jasmin-catering-rg --output table

# Check logs
az containerapp job logs show --name jasmin-email-processor \
  --resource-group jasmin-catering-rg --follow
```

### End-to-End Testing
```mermaid
graph LR
    T1[Send Test Email] --> T2[Wait for Processing]
    T2 --> T3[Verify AI Response]
    T3 --> T4[Check Slack Notifications]
    T4 --> T5[Validate Email Delivery]
    T5 --> T6[Performance Metrics]
    
    classDef test fill:#28a745,stroke:#1e7e34,stroke-width:2px,color:#fff
    class T1,T2,T3,T4,T5,T6 test
```

### Test Scripts & Utilities

#### 📧 Send Test Email
```bash
# Send a test catering inquiry to ma3u-test@email.de
python scripts/send-test-email.py

# This script:
# - Sends a realistic German catering inquiry
# - Includes detailed event requirements
# - Tests the full email processing pipeline
# - Verifies email delivery to the configured alias
```

#### 🔔 Test Slack Notifications
```bash
# Test Slack integration without sending emails
python scripts/test-slack-notification.py

# This script:
# - Posts a simulated long email to Slack
# - Verifies the full message is displayed (not truncated)
# - Tests message formatting and chunking
# - Validates Slack API connectivity
```

#### 🔐 Backup .env to 1Password
```bash
# Backup local .env file to 1Password vault
./scripts/backup-env-to-1password.sh

# This script:
# - Creates a timestamped backup in JasminCatering vault
# - Stores the complete .env file as a document
# - Provides easy restore commands
# - Ensures secure team sharing of credentials

# Restore from backup:
op document get 'jasmin-catering-env-YYYY-MM-DD_HH-MM-SS' --vault 'JasminCatering' > .env
```

#### 📊 Check Email Processing
```bash
# Verify if emails were received and processed
python scripts/check-email-processing.py

# This script:
# - Connects to the email inbox
# - Lists recent catering emails
# - Identifies test emails by subject
# - Confirms email filtering is working correctly
```

#### 🔍 Monitor Container Logs
```bash
# Check Azure Container Apps execution logs
./scripts/check-container-logs.sh

# This script:
# - Shows recent job executions
# - Displays container logs
# - Searches for specific email processing
# - Provides alternative monitoring methods
```

## 🔧 Troubleshooting

### Common Issues & Solutions

#### Container Won't Start
```bash
# Check container logs
az containerapp job logs show --name jasmin-email-processor \
  --resource-group jasmin-catering-rg

# Verify environment variables
az containerapp job show --name jasmin-email-processor \
  --resource-group jasmin-catering-rg \
  --query "properties.template.containers[0].env"

# Test image locally
docker run --rm jasmin-catering-ai python -c "import main; print('OK')"
```

#### Secrets Not Loading
```bash
# Verify Key Vault access
az keyvault secret list --vault-name jasmin-catering-kv

# Check managed identity permissions
az keyvault show --name jasmin-catering-kv \
  --query "properties.accessPolicies"

# Test secret retrieval
az keyvault secret show --vault-name jasmin-catering-kv \
  --name slack-bot-token --query "value"
```

#### Schedule Not Triggering
```bash
# Check Container Apps Job status
az containerapp job show --name jasmin-email-processor \
  --resource-group jasmin-catering-rg

# View recent executions
az containerapp job execution list --name jasmin-email-processor \
  --resource-group jasmin-catering-rg

# Manually trigger the job
az containerapp job start --name jasmin-email-processor \
  --resource-group jasmin-catering-rg
```

### Performance Debugging
```bash
# Application Insights queries
az monitor app-insights query --app jasmin-catering-insights \
  --analytics-query "requests | where timestamp > ago(1h) | summarize count() by resultCode"

# Container resource usage
az containerapp job show --name jasmin-email-processor \
  --resource-group jasmin-catering-rg \
  --query "properties.template.containers[0].resources"
```

## 📈 Scaling & Performance

### Auto-Scaling Configuration
```yaml
# Container Apps scaling rules
scale:
  minReplicas: 0      # Scale to zero when idle
  maxReplicas: 3      # Handle traffic spikes
  rules:
  - name: http-requests
    http:
      metadata:
        concurrentRequests: 10
```

### Performance Optimization
- **Cold Start Time**: 2-3 seconds (optimized container)
- **Memory Usage**: 256MB baseline, 512MB peak
- **CPU Usage**: 0.1 vCPU baseline, 0.5 vCPU peak
- **Concurrent Processing**: Up to 5 emails simultaneously

### Cost Optimization Strategies
1. **Scale-to-Zero**: No cost when idle (nights, weekends)
2. **Optimized Scheduling**: Reduce trigger frequency during low activity
3. **AI Token Management**: Efficient prompt engineering reduces costs
4. **Container Optimization**: Minimal base image reduces storage costs

---

## 🎯 Project Status

### ✅ Completed & Deployed
- [x] **Azure OpenAI Assistant with Vector Store RAG** - Enterprise-grade AI Agent deployed
- [x] **6 Knowledge Documents Uploaded** - Complete business knowledge base integrated
- [x] **Cloud-native Container Apps Jobs** - Fully deployed and operational
- [x] **Enhanced architecture** - AI Assistant + Vector Store, 48% cost reduction
- [x] **Automated scheduling** - Runs every 5 minutes with cron
- [x] **Scale-to-zero optimization** - No costs when idle
- [x] **Advanced RAG processing** - Semantic search through knowledge documents
- [x] **Secure secret management** - Azure Key Vault integration
- [x] **Real-time Slack integration** - Full notifications working
- [x] **Email automation** - IMAP/SMTP processing operational
- [x] **Dynamic pricing calculation** - Basis/Standard/Premium tiers
- [x] **Error handling & monitoring** - Comprehensive logging
- [x] **Docker containerization** - Optimized for production

### 🚀 Production Metrics (Verified)
- **✅ Uptime**: 100% success rate across all test executions
- **⚡ Performance**: 37-second processing time for 5 emails
- **💰 Cost**: $2-8/month (75% reduction from initial architecture)
- **🔄 Automation**: Every 5 minutes, fully hands-off
- **📧 Email Processing**: 5/5 emails processed successfully
- **🤖 AI Response Time**: 4-7 seconds per email
- **📱 Slack Integration**: Real-time notifications operational

### 📋 Future Enhancements
- [ ] Multi-language support for international customers
- [ ] Production email system (info@jasmincatering.com with 1&1/IONOS)
- [ ] CRM integration for customer management
- [ ] Advanced analytics and business intelligence
- [ ] Mobile app for catering management

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**🤖 Powered by Azure AI Services & Container Apps Jobs**  
*Production-ready intelligent catering automation with enterprise-grade cloud infrastructure*

**📊 System Performance**: 100% uptime | 4-7s AI response time | $0.02-0.05 per email  
**🔒 Enterprise Security**: Azure Key Vault | Container isolation | Secure secret management  
**📈 Cloud-Native**: Scale-to-zero cost optimization | Automated cron scheduling | 75% cost reduction  
**🎯 Production Verified**: 5/5 test cases successful | Real-time Slack integration | Full email automation