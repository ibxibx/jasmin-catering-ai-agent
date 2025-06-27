# 🍽️ Jasmin Catering AI Agent

## 🚀 **Current Implementation: Azure Logic Apps + AI Foundry**

Automated email processing system for Jasmin Catering - a Syrian fusion restaurant in Berlin. The system monitors emails sent to `ma3u-test@email.de`, generates professional catering offers in German using GPT-4 through Azure AI Foundry, and creates email drafts for review.

### ✅ **What's Working Now:**
- **Email Filtering**: Only processes emails sent TO `ma3u-test@email.de`
- **AI Processing**: Azure AI Foundry (GPT-4) for intelligent response generation
- **Automated Offers**: Calculates pricing based on guest count (35-45€/person)
- **German Templates**: Professional responses with Syrian fusion menu suggestions
- **Sweden Central Region**: Default deployment target due to Azure restrictions

---

## 📁 **Project Structure**

```
jasmin-catering-ai-agent/
├── README.md                       # This documentation
├── CLAUDE.md                       # Guide for future Claude instances
├── .env                           # Environment configuration (not in Git)
├── .gitignore                     # Git ignore rules
├── deployments/                   # All deployment assets
│   ├── scripts/                   # Deployment and utility scripts
│   │   ├── deploy-main.sh        # Main deployment script
│   │   ├── deploy-ai-foundry.sh  # AI Foundry deployment script
│   │   ├── load-env-config.sh    # Environment configuration loader
│   │   ├── monitor-logic-app.sh  # Monitoring script
│   │   ├── send-test-email.sh    # Test email information script
│   │   └── send-test-email.py    # Python test email sender
│   ├── logic-apps/               # Logic App workflow definitions
│   │   ├── email-processor-workflow.json  # Main workflow definition
│   │   └── ai-foundry-workflow.json       # AI Foundry specific workflow
│   ├── archive/                  # Experimental/deprecated scripts
│   │   ├── scripts/              # Archived Python and shell scripts
│   │   ├── logic-apps/           # Archived workflow definitions
│   │   └── README.md             # Archive documentation
│   ├── terraform/                # Infrastructure as Code (Terraform)
│   │   ├── main.tf              # Main Terraform configuration
│   │   ├── variables.tf         # Variable definitions
│   │   ├── outputs.tf           # Output definitions
│   │   ├── logic_app_complete.tf # Complete Logic App deployment
│   │   ├── terraform.tfvars.example # Example variables file
│   │   ├── README.md            # Terraform documentation
│   │   └── .gitignore           # Terraform-specific ignores
│   └── templates/                # Email templates and examples
│       └── email-draft-example.md
└── docs/                         # Additional documentation
```

---

## 🏗️ **Architecture**

```mermaid
graph TD
    A[📧 Email Inbox] --> B{🔍 Filter}
    B -->|TO: ma3u-test@email.de| C[✅ Process Email]
    B -->|Other Recipients| D[❌ Ignore]
    C --> E[🤖 Azure AI Foundry]
    E --> F[📝 Generate Offer]
    F --> G[💾 Store Draft]
    G --> H[📤 Ready for Review]
    
    subgraph "Azure AI Platform"
        E
        N[AI Project:<br/>jasmin-catering]
        O[AI Services Resource]
        J[GPT-4 Model]
    end
    
    subgraph "Logic App"
        I[Sweden Central<br/>Region]
        B
        C
    end
    
    subgraph "Processing Steps"
        K[Extract Details]
        L[Calculate Pricing]
        M[Generate German Response]
    end
```

---

## 🚀 **Quick Start**

### **Prerequisites**
- Azure CLI installed (`brew install azure-cli`)
- Azure subscription with access
- `.env` file with required credentials

### **1. Clone & Configure**
```bash
git clone [repository-url]
cd jasmin-catering-ai-agent

# Create .env file with your credentials
cp .env.example .env
# Edit .env with your values
```

### **2. Deploy**
```bash
cd deployments/scripts
./deploy-main.sh
```

### **3. Monitor**
```bash
./monitor-logic-app.sh
```

---

## 🔧 **Deployment Options**

### **Option 1: Shell Scripts (Recommended)**

The deployment scripts have been cleaned and organized. Only production-ready scripts remain in the main directories.

| Script | Purpose | Usage |
|--------|---------|-------|
| `deploy-ai-foundry.sh` | Deploy with AI Foundry integration | `./deploy-ai-foundry.sh` |
| `deploy-main.sh` | Basic deployment script | `./deploy-main.sh` |
| `load-env-config.sh` | Loads environment configuration | Sourced by other scripts |
| `monitor-logic-app.sh` | Monitors Logic App runs | `./monitor-logic-app.sh` |
| `send-test-email.sh` | Shows test email configuration | `./send-test-email.sh` |
| `send-test-email.py` | Python script to send test emails | `python send-test-email.py` |

**Note**: Experimental scripts (Assistant API, RAG, vector DB) have been moved to `deployments/archive/`

### **Option 2: Terraform (Infrastructure as Code)**

For production deployments, use the Terraform configuration in `deployments/terraform/`:

```bash
cd deployments/terraform

# Initialize Terraform
terraform init

# Copy and configure variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# Plan deployment
terraform plan

# Apply configuration
terraform apply
```

**Benefits of Terraform:**
- Declarative infrastructure definition
- State management and version control
- Easy rollback and disaster recovery
- Better team collaboration
- Modular and reusable code

See `deployments/terraform/README.md` for detailed Terraform documentation.

---

## 🤖 **AI Service: Azure AI Foundry**

We use **Azure AI Foundry** for AI capabilities:

1. **Unified Platform**: AI Foundry provides a comprehensive AI development platform
2. **Project Management**: Organized AI resources under the `jasmin-catering` project
3. **Model Access**: Direct access to GPT-4 and other models
4. **Integration**: Seamless integration with other Azure AI services

**Technical Details:**
- **AI Project**: jasmin-catering
- **Resource**: jasmin-catering-resource (AI Services)
- **Endpoint**: The AI Foundry project uses the underlying AI Services endpoint
- **API Format**: OpenAI-compatible REST API

**Endpoint Format:**
```
https://jasmin-catering-resource.cognitiveservices.azure.com/openai/deployments/gpt-4o/chat/completions
```

*Note: AI Foundry projects utilize AI Services infrastructure, which is why the endpoint appears as a Cognitive Services URL. This is the standard Azure AI architecture.*

---

## 🌍 **Region: Sweden Central**

**Default Region**: `swedencentral`

Due to Azure restrictions in West Europe, all deployments default to Sweden Central. This is configured in:
- `load-env-config.sh`: Sets default region
- `deploy-main.sh`: Forces Sweden Central
- Resource group: `logicapp-jasmin-sweden_group`

---

## 📊 **Monitoring & Testing**

### **Check Deployment Status:**
```bash
az logic workflow show \
  --resource-group logicapp-jasmin-sweden_group \
  --name jasmin-order-processor-sweden \
  --query state
```

### **View Recent Runs:**
```bash
./monitor-logic-app.sh
```

### **Test Email Processing:**
Since the Logic App uses a timer trigger and simulates emails, you can:

1. **View test email information:**
   ```bash
   ./deployments/scripts/send-test-email.sh
   ```

2. **Monitor Logic App runs (real-time):**
   ```bash
   # List recent runs
   az rest --method get \
     --uri "https://management.azure.com/subscriptions/$AZURE_SUBSCRIPTION_ID/resourceGroups/logicapp-jasmin-sweden_group/providers/Microsoft.Logic/workflows/jasmin-order-processor-sweden/runs?api-version=2019-05-01&\$top=5" \
     --query "value[0:5].{Name:name,Status:properties.status,StartTime:properties.startTime}" \
     --output table
   ```

---

## 🔐 **Configuration (.env)**

Required environment variables:
```bash
# Azure
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=logicapp-jasmin-catering_group
AZURE_AI_API_KEY=your-api-key

# Email
WEBDE_EMAIL_ALIAS=ma3u-test@email.de
WEBDE_APP_PASSWORD=your-app-password
```

---

## 🚨 **Important Notes**

1. **Email Filter**: Only processes emails sent TO `ma3u-test@email.de`
2. **Region**: Always uses Sweden Central (West Europe restricted)
3. **API Key**: Stored in `.env`, never in code
4. **Pricing**: Calculated at 35-45€ per person
5. **Language**: All customer communication in German

---

## 🛠️ **Troubleshooting**

### **Deployment Fails**
- Check Azure login: `az login`
- Verify subscription: `az account show`
- Ensure `.env` file exists with all variables

### **No Emails Processed**
- Verify email is sent TO `ma3u-test@email.de`
- Check Logic App is enabled
- Review filter conditions in workflow

### **AI Errors**
- Verify API key in `.env`
- Check endpoint URL format
- Ensure Cognitive Services resource exists

---

## 📈 **Next Steps**

1. **Production Email**: Migrate from test to `info@jasmincatering.com`
2. **IMAP Integration**: Replace simulation with real email monitoring
3. **Approval Workflow**: Add Teams/Slack approval before sending
4. **SMTP Sending**: Automated email responses

---

## 👥 **Contributing**

1. Check `CLAUDE.md` for AI assistant guidance
2. Follow existing code patterns
3. Test deployments in Sweden Central
4. Update documentation for changes

---

Built for Jasmin Catering - Syrian Fusion Cuisine in Berlin 🇸🇾🇩🇪