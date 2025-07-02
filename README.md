# Jasmin Catering AI Agent

An intelligent email processing system that automatically responds to catering inquiries using Azure AI services. The system processes emails sent to `ma3u-test@email.de`, generates professional catering offers in German, and sends responses back to customers.

## 🏗️ Architecture Overview

```
📧 Customer Email → 🔄 AI Processing → 📤 Automated Response
    (Inquiry)         (Azure Logic Apps      (Professional Offer)
                      + Azure OpenAI)
```

## 📋 Table of Contents

- [Azure Resources Deployed](#azure-resources-deployed)
- [Azure Key Vault Configuration](#azure-key-vault-configuration)
- [Workflow Sequential Process](#workflow-sequential-process)
- [Getting Started with Azure](#getting-started-with-azure)
- [Project Status](#project-status)
- [Prerequisites](#prerequisites)
- [Deployment Guide](#deployment-guide)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

## 🏢 Azure Resources Deployed

### 1. Resource Group
- **Name**: `logicapp-jasmin-sweden_group`
- **Location**: Sweden Central
- **Purpose**: Container for all project resources
- **Learn More**: [Azure Resource Groups](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/manage-resource-groups-portal)

### 2. Azure Logic Apps
#### Main Logic App: `jasmin-order-processor-sweden`
- **Type**: Consumption Logic App
- **Location**: Sweden Central  
- **Trigger**: Recurrence (every 5 minutes)
- **Purpose**: Processes simulated email queues and generates AI responses
- **Learn More**: [Azure Logic Apps](https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-overview)

#### Test Logic App: `jasmin-email-test-sender`
- **Type**: Consumption Logic App
- **Location**: Sweden Central
- **Trigger**: Manual HTTP trigger
- **Purpose**: Processes test email scenarios for demonstration
- **Learn More**: [Logic Apps Triggers](https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-workflow-actions-triggers)

### 3. Azure OpenAI Service
- **Name**: `jasmin-catering-ai`
- **SKU**: S0 (Standard)
- **Location**: Sweden Central
- **Model Deployed**: GPT-4o (2024-05-13)
- **Deployment Name**: `gpt-4o`
- **Purpose**: Generates intelligent catering responses
- **Learn More**: [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/overview)

### 4. Azure Key Vault
- **Name**: `jasmin-catering-kv`
- **Location**: Sweden Central
- **Access Policy**: Classic access policies enabled
- **Purpose**: Securely stores credentials and API keys
- **Learn More**: [Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/overview)

## 🔐 Azure Key Vault Configuration

The following secrets are stored in `jasmin-catering-kv`:

| Secret Name | Purpose | Example Value |
|-------------|---------|---------------|
| `azure-subscription-id` | Azure subscription identifier | `6576090b-36b2-4ba1-94ae-d2f52eed2789` |
| `azure-tenant-id` | Azure AD tenant identifier | `b4b6ea88-f8b8-4539-a42d-b5e46434242b` |
| `azure-user-email` | Azure account email | `matthias.buchhorn@web.de` |
| `azure-ai-api-key` | OpenAI service API key | `2862cfed401f41f990fc67ea952c2a8d` |
| `from-email-address` | Sender email address | `matthias.buchhorn@web.de` |
| `from-email-password` | Email app-specific password | `SLFYZ5QN3PP6ZP575C4L` |
| `webde-app-password` | Web.de SMTP authentication | `SLFYZ5QN3PP6ZP575C4L` |

### Accessing Key Vault Secrets
```bash
# List all secrets
az keyvault secret list --vault-name "jasmin-catering-kv"

# Get a specific secret
az keyvault secret show --vault-name "jasmin-catering-kv" --name "azure-ai-api-key"
```

**Learn More**: [Key Vault Secret Management](https://learn.microsoft.com/en-us/azure/key-vault/secrets/about-secrets)

## 🔄 Workflow Sequential Process

### Phase 1: Email Reception (Simulated)
1. **Timer Trigger**: Logic App runs every 5 minutes
2. **Email Queue**: Simulated test emails are created in the workflow
3. **Filtering**: Only emails to `ma3u-test@email.de` are processed

### Phase 2: AI Processing
1. **Email Extraction**: Relevant email details are extracted
2. **AI API Call**: Request sent to Azure OpenAI GPT-4o model
3. **Prompt Engineering**: System prompt configures AI as Jasmin Catering consultant
4. **Response Generation**: AI creates professional German catering offers

### Phase 3: Response Formatting
1. **Template Application**: Response includes company branding
2. **Three-Tier Pricing**: Basis (25-35€), Standard (35-45€), Premium (50-70€)
3. **Personalization**: Addresses specific customer requirements

### Phase 4: Email Delivery (Simulated)
1. **Draft Creation**: Response is prepared but not sent via SMTP
2. **Logging**: Transaction details are stored for monitoring
3. **Status Tracking**: Success/failure status is recorded

### Real Email Processing (Manual Script)
For actual email processing, use the Python scripts:
```bash
# Send test inquiry emails
python send-catering-emails.py

# Process and respond to emails
python process-all-emails.py
```

## 🚀 Getting Started with Azure

### 1. Azure Account Setup
- **Create Account**: [Azure Free Account](https://azure.microsoft.com/free/)
- **Azure CLI**: [Install Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
- **Authentication**: [Azure CLI Login](https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli)

### 2. Required Azure Services
- **Logic Apps**: [Logic Apps Pricing](https://azure.microsoft.com/pricing/details/logic-apps/)
- **OpenAI Service**: [OpenAI Service Pricing](https://azure.microsoft.com/pricing/details/cognitive-services/openai-service/)
- **Key Vault**: [Key Vault Pricing](https://azure.microsoft.com/pricing/details/key-vault/)

### 3. Azure Regions
This project uses **Sweden Central** due to GPT-4o availability.
- **Check Availability**: [Azure Products by Region](https://azure.microsoft.com/global-infrastructure/services/)

## ✅ Project Status

### ✅ Completed Tasks

#### Infrastructure & Authentication
- [x] Azure subscription setup and authentication
- [x] Resource group creation in Sweden Central
- [x] Azure CLI configuration and login
- [x] Environment variables configuration in `.env`
- [x] Azure Key Vault deployment and secret storage

#### AI Services
- [x] Azure OpenAI service deployment
- [x] GPT-4o model deployment and configuration
- [x] AI prompt engineering for catering responses
- [x] Three-tier pricing system implementation

#### Logic Apps Development
- [x] Main Logic App workflow creation
- [x] Test Logic App for email scenarios
- [x] Email filtering and processing logic
- [x] AI integration and response generation
- [x] Error handling and logging

#### Email Integration
- [x] Web.de SMTP configuration and testing
- [x] Email authentication with app-specific passwords
- [x] Test email sending functionality
- [x] Real email processing with Python scripts
- [x] End-to-end email workflow testing

#### Testing & Validation
- [x] 5 diverse test email scenarios created
- [x] AI response generation testing
- [x] Email delivery confirmation
- [x] Professional German language responses
- [x] Customer-specific requirement handling

### 🔄 In Progress Tasks

#### Email Automation
- [ ] Real-time email polling integration in Logic Apps
- [ ] IMAP connector configuration for live email processing
- [ ] Automatic email response sending via Logic Apps

#### Production Readiness
- [ ] Production email system integration (info@jasmincatering.com)
- [ ] 1&1/IONOS email configuration
- [ ] SSL certificate and domain setup

### 📋 Pending Tasks

#### Enhanced AI Capabilities
- [ ] RAG (Retrieval Augmented Generation) system implementation
- [ ] Document upload to Azure AI Studio vector store
- [ ] Business knowledge base integration
- [ ] Menu and pricing database connection

#### Monitoring & Operations
- [ ] Azure Monitor alerts and dashboards
- [ ] Application Insights integration
- [ ] Performance monitoring and optimization
- [ ] Cost monitoring and optimization

#### Advanced Features
- [ ] Customer follow-up automation
- [ ] CRM system integration
- [ ] Multi-language support
- [ ] Booking confirmation system
- [ ] Payment processing integration

#### Security & Compliance
- [ ] Azure Active Directory integration
- [ ] Role-based access control (RBAC)
- [ ] Data encryption at rest
- [ ] GDPR compliance measures
- [ ] Audit logging and compliance reporting

## 📚 Prerequisites

### Required Tools
- **Azure CLI**: [Installation Guide](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
- **Python 3.8+**: For email processing scripts
- **Git**: For version control

### Required Knowledge
- **Basic Azure Concepts**: [Azure Fundamentals](https://learn.microsoft.com/en-us/training/paths/azure-fundamentals/)
- **Logic Apps Basics**: [Logic Apps Learning Path](https://learn.microsoft.com/en-us/training/paths/build-workflows-with-logic-apps/)
- **AI Services Overview**: [AI Services Learning Path](https://learn.microsoft.com/en-us/training/paths/get-started-with-artificial-intelligence-on-azure/)

### Azure Permissions Required
- **Contributor** role on the subscription
- **Key Vault Administrator** for secret management
- **Cognitive Services Contributor** for AI services

## 🚀 Deployment Guide

### 1. Clone Repository
```bash
git clone <repository-url>
cd jasmin-catering-ai-agent
```

### 2. Configure Environment
```bash
# Copy and edit environment file
cp .env.example .env
# Edit .env with your credentials
```

### 3. Azure Login
```bash
az login
az account set --subscription "your-subscription-id"
```

### 4. Deploy Resources
```bash
# Make deployment script executable
chmod +x deployments/scripts/deploy-main.sh

# Run deployment
./deployments/scripts/deploy-main.sh
```

### 5. Test Email System
```bash
# Install Python dependencies
pip install -r requirements.txt

# Send test emails
python send-catering-emails.py

# Process responses
python process-all-emails.py
```

## 🔧 Troubleshooting

### Common Issues

#### Authentication Errors
- **Issue**: `Authentication credentials invalid`
- **Solution**: Regenerate app-specific password in web.de settings
- **Reference**: [Web.de App Passwords](https://hilfe.web.de/email/sicherheit/app-passwort.html)

#### Logic App Deployment Failures
- **Issue**: Resource not found errors
- **Solution**: Ensure resource group exists and correct region is selected
- **Reference**: [Logic Apps Troubleshooting](https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-troubleshoot-and-diagnose-workflow-failures)

#### OpenAI API Errors
- **Issue**: Model not available in region
- **Solution**: Use Sweden Central or other supported regions
- **Reference**: [OpenAI Model Availability](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models)

### Debugging Commands
```bash
# Check Logic App status
az logic workflow show --resource-group "logicapp-jasmin-sweden_group" --name "jasmin-order-processor-sweden"

# View Key Vault secrets
az keyvault secret list --vault-name "jasmin-catering-kv"

# Test email configuration
python test-webde-auth.py
```

## 🎯 Next Steps

### Immediate Actions (Next 1-2 weeks)
1. **Implement real-time email processing** in Logic Apps
2. **Set up production email** integration with info@jasmincatering.com
3. **Deploy monitoring dashboards** for operational visibility

### Short-term Goals (Next 1-2 months)
1. **RAG system implementation** for enhanced AI responses
2. **Customer follow-up automation** for unconfirmed offers
3. **Performance optimization** and cost management

### Long-term Vision (Next 3-6 months)
1. **Multi-channel support** (WhatsApp, web forms, social media)
2. **Advanced analytics** and business intelligence
3. **Integration with booking and payment systems**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For questions or issues:
- **Azure Support**: [Azure Support Plans](https://azure.microsoft.com/support/plans/)
- **Documentation**: [Azure Documentation](https://learn.microsoft.com/en-us/azure/)
- **Community**: [Azure Community](https://techcommunity.microsoft.com/t5/azure/ct-p/Azure)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🤖 Powered by Azure AI Services**  
*Automatically generating professional catering responses since 2025*