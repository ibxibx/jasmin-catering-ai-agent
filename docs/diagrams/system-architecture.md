# System Architecture Diagrams

## Complete Cloud Architecture

```mermaid
graph TB
    subgraph "External Systems"
        subgraph "Customer Communication"
            CUSTOMERS[👥 Customers<br/>Catering Inquiries]
            EMAIL_SYS[📧 Email System<br/>web.de<br/>IMAP/SMTP]
        end
        
        subgraph "Business Communication" 
            SLACK_WS[💬 Slack Workspace<br/>#requests-and-responses<br/>#jasmin-catering-logs]
        end
    end

    subgraph "Azure Cloud Environment - Sweden Central"
        subgraph "Container Platform"
            subgraph "Container Apps Environment"
                CONT_JOB[⚡ Container Apps Job<br/>jasmin-email-processor<br/>Cron: */5 * * * *<br/>Scale-to-Zero]
                CONT_ENV[🔧 Container Environment<br/>jasmin-catering-env<br/>Auto-scaling: 0-3 replicas]
            end
            
            subgraph "Container Registry"
                ACR[📦 Azure Container Registry<br/>jasmincateringregistry<br/>Docker Image Storage]
            end
        end

        subgraph "AI & Machine Learning"
            subgraph "Azure OpenAI Service"
                AI_SERVICE[🤖 Azure OpenAI<br/>jasmin-openai-372bb9<br/>GPT-4.1 Deployment<br/>50 RPM Rate Limit]
                
                AI_ASSISTANT[🧠 AI Assistant<br/>asst_UHTUDffJEyLQ6qexElqOopac<br/>Jasmin Catering Agent<br/>File Search Tool]
                
                VECTOR_STORE[📚 Vector Store<br/>vs_xDbEaqnBNUtJ70P7GoNgY1qD<br/>AssistantVectorStore_Jasmin<br/>6 Knowledge Documents]
            end
        end

        subgraph "Security & Secrets"
            KEY_VAULT[🔐 Azure Key Vault<br/>jasmin-catering-kv<br/>Secrets Management<br/>Managed Identity Access]
        end

        subgraph "Knowledge Base"
            subgraph "Business Documents"
                DOC1[📄 catering-brief.md<br/>Business Process]
                DOC2[💰 business-conditions.md<br/>Pricing & Terms]  
                DOC3[🥬 vegetarian-offer-template.md<br/>Vegetarian Options]
                DOC4[✍️ response-examples.md<br/>Professional Examples]
                DOC5[📧 email-template.md<br/>Communication Standards]
                DOC6[🎯 jasmin_catering_prompt.md<br/>Agent Instructions]
            end
        end
    end

    %% External Connections
    CUSTOMERS -.->|Send Inquiries| EMAIL_SYS
    EMAIL_SYS -.->|Auto Response| CUSTOMERS

    %% Container Job Connections
    CONT_JOB -->|Fetch Emails| EMAIL_SYS
    CONT_JOB -->|Send Responses| EMAIL_SYS
    CONT_JOB -->|Post Updates| SLACK_WS
    CONT_JOB -->|Get Secrets| KEY_VAULT

    %% AI Processing Flow
    CONT_JOB -->|Process with AI| AI_ASSISTANT
    AI_ASSISTANT -->|Search Knowledge| VECTOR_STORE
    VECTOR_STORE -->|Access Documents| DOC1
    VECTOR_STORE -->|Access Documents| DOC2
    VECTOR_STORE -->|Access Documents| DOC3
    VECTOR_STORE -->|Access Documents| DOC4
    VECTOR_STORE -->|Access Documents| DOC5
    VECTOR_STORE -->|Access Documents| DOC6
    VECTOR_STORE -->|Return Context| AI_ASSISTANT
    AI_ASSISTANT -->|Generate Response| CONT_JOB

    %% Infrastructure Connections
    ACR -.->|Pull Image| CONT_JOB
    CONT_ENV -.->|Host| CONT_JOB
    AI_SERVICE -.->|Hosts| AI_ASSISTANT
    AI_SERVICE -.->|Manages| VECTOR_STORE

    %% Styling
    classDef external fill:#e8f5e8,stroke:#4caf50,stroke-width:2px,color:#1b5e20
    classDef container fill:#e3f2fd,stroke:#2196f3,stroke-width:2px,color:#0d47a1
    classDef ai fill:#fff3e0,stroke:#ff9800,stroke-width:2px,color:#e65100
    classDef security fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px,color:#4a148c
    classDef docs fill:#f1f8e9,stroke:#8bc34a,stroke-width:2px,color:#33691e

    class CUSTOMERS,EMAIL_SYS,SLACK_WS external
    class CONT_JOB,CONT_ENV,ACR container
    class AI_SERVICE,AI_ASSISTANT,VECTOR_STORE ai
    class KEY_VAULT security
    class DOC1,DOC2,DOC3,DOC4,DOC5,DOC6 docs
```

## Data Flow Architecture

```mermaid
graph LR
    subgraph "Input Layer"
        EMAIL_IN[📧 Incoming Emails<br/>Customer Inquiries]
        SECRETS[🔐 Secrets & Config<br/>Azure Key Vault]
    end

    subgraph "Processing Layer"
        subgraph "Application Core"
            MAIN[🚀 main.py<br/>Entry Point]
            EMAIL_PROC[📬 EmailProcessor<br/>IMAP/SMTP Handler]
            AI_AGENT[🤖 AIAssistantOpenAI<br/>Enhanced RAG]
            SLACK_NOT[💬 SlackNotifier<br/>Real-time Updates]
        end
    end

    subgraph "AI Layer"
        subgraph "Azure OpenAI"
            ASSISTANT[🧠 AI Assistant<br/>Thread Management]
            SEARCH[🔍 File Search Tool<br/>Vector Store Query]
            KNOWLEDGE[📚 Knowledge Base<br/>6 Documents]
        end
    end

    subgraph "Output Layer"
        EMAIL_OUT[📤 Outgoing Emails<br/>Professional Responses]
        SLACK_OUT[📱 Slack Notifications<br/>Monitoring & Logs]
        METRICS[📊 Processing Metrics<br/>Performance Data]
    end

    %% Data Flow
    EMAIL_IN --> EMAIL_PROC
    SECRETS --> MAIN
    MAIN --> EMAIL_PROC
    EMAIL_PROC --> AI_AGENT
    AI_AGENT --> ASSISTANT
    ASSISTANT --> SEARCH
    SEARCH --> KNOWLEDGE
    KNOWLEDGE --> SEARCH
    SEARCH --> ASSISTANT
    ASSISTANT --> AI_AGENT
    AI_AGENT --> EMAIL_PROC
    AI_AGENT --> SLACK_NOT
    EMAIL_PROC --> EMAIL_OUT
    SLACK_NOT --> SLACK_OUT
    AI_AGENT --> METRICS

    %% Styling
    classDef input fill:#e8f5e8,stroke:#4caf50,stroke-width:2px
    classDef process fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    classDef ai fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    classDef output fill:#fce4ec,stroke:#e91e63,stroke-width:2px

    class EMAIL_IN,SECRETS input
    class MAIN,EMAIL_PROC,AI_AGENT,SLACK_NOT process
    class ASSISTANT,SEARCH,KNOWLEDGE ai
    class EMAIL_OUT,SLACK_OUT,METRICS output
```

## Infrastructure Components

### 🏗️ Container Platform
- **Container Apps Job**: Scheduled execution every 5 minutes
- **Auto-scaling**: 0-3 replicas based on demand
- **Cost Optimization**: Scale-to-zero when idle

### 🤖 AI Services  
- **Azure OpenAI**: GPT-4.1 deployment with enhanced capabilities
- **AI Assistant**: Persistent context and conversation management
- **Vector Store**: Semantic search through business knowledge

### 🔐 Security
- **Managed Identity**: Secure service-to-service authentication
- **Key Vault**: Centralized secret management
- **Network Security**: VNet integration for production workloads

### 📊 Monitoring
- **Real-time Notifications**: Slack integration for all activities
- **Performance Metrics**: Processing time, success rates, token usage
- **Error Handling**: Comprehensive logging and alerting

## Cost Structure

| Component | Monthly Cost | Optimization |
|-----------|-------------|--------------|
| Container Apps Jobs | $2-8 | Scale-to-zero |
| Azure OpenAI | $50-80 | Pay-per-use tokens |
| Key Vault | $3 | Operation-based pricing |
| Container Registry | $5 | Minimal storage |
| **Total** | **$60-96** | **48% reduction** |

## Performance Characteristics

- **Latency**: 9.93s average processing time
- **Throughput**: 50 requests per minute
- **Availability**: 99.9% SLA target
- **Scalability**: Auto-scaling based on email volume
- **Reliability**: Retry logic and error handling