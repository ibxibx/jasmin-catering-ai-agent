# 📁 Project Structure Guide

## Overview

This document explains the organized structure of the Jasmin Catering AI Agent project after restructuring for better maintainability and clarity.

## 🏗️ Directory Structure

```
jasmin-catering-ai-agent/
├── 📁 config/                          # Configuration Management
│   └── settings.py                     # Centralized app configuration
│
├── 📁 core/                            # Core Application Logic
│   ├── email_processor.py              # IMAP/SMTP email handling
│   ├── ai_assistant_openai_agent.py    # Enhanced RAG AI Assistant (ACTIVE)
│   ├── ai_assistant.py                 # Legacy AI assistant
│   ├── ai_assistant_rag.py             # Legacy RAG implementation
│   ├── ai_assistant_agent.py           # Legacy agent implementation
│   └── slack_notifier.py               # Slack integration
│
├── 📁 deployments/                     # Azure Deployment Assets
│   ├── documents/                      # Knowledge Base Files
│   │   ├── business-conditions.md      # Pricing & business terms
│   │   ├── catering-brief.md           # Business process guide
│   │   ├── email-template.md           # Communication standards
│   │   ├── jasmin_catering_prompt.md   # AI agent instructions
│   │   ├── response-examples.md        # Professional examples
│   │   └── vegetarian-offer-template.md # Vegetarian options
│   └── templates/                      # Configuration Templates
│       ├── company-policies.md         # Business policies
│       └── order-templates.md          # Order templates
│
├── 📁 docs/                            # Documentation
│   ├── diagrams/                       # Architecture & Workflow Diagrams
│   │   ├── system-architecture.md      # Complete system architecture
│   │   └── sequential-workflow.md      # Step-by-step workflow
│   ├── azure-ai-agent-deployment.md    # AI deployment guide
│   ├── enhanced-rag-system.md          # RAG system documentation
│   ├── CLEANUP-SUMMARY.md              # Resource cleanup guide
│   ├── KNOWLEDGE-UPLOAD-SUCCESS.md     # Knowledge upload results
│   └── PROJECT_STATUS.md               # Current project status
│
├── 📁 scripts/                         # All Scripts Consolidated Here
│   ├── deployment/                     # Azure Deployment Scripts
│   │   ├── deploy-container-jobs.sh    # Main Container Apps deployment
│   │   ├── deploy-to-azure.sh          # Alternative deployment
│   │   └── deploy-with-ai-foundry.sh   # AI Foundry deployment
│   ├── testing/                        # Test Scripts & Results
│   │   ├── test-enhanced-rag-system.py # RAG system testing
│   │   ├── send_test_emails.py        # Send test emails utility
│   │   └── test-results-*.json         # Test execution results
│   ├── utilities/                      # Helper & Utility Scripts
│   │   ├── document-indexer.py         # Azure AI Search indexer
│   │   ├── upload-files-rest-api.py    # Vector store file upload
│   │   ├── verify-knowledge-upload.py  # Upload verification
│   │   ├── check-vectorstore-direct.py # Direct vector store check
│   │   └── update-container-job-config.sh # Config updates
│   ├── archive/                        # Deprecated/Unused Scripts
│   │   ├── add-ai-agents-support.sh    # Legacy AI agents script
│   │   ├── cleanup-*.sh                # Old cleanup scripts
│   │   ├── create-ai-agent-*.py        # Legacy agent creation
│   │   └── upload-knowledge-when-available.py # Old upload script
│   ├── load-env-config.sh              # Environment configuration loader
│   ├── monitor-real-emails.py          # Real email monitoring
│   ├── process-all-emails.py           # Email processing utility
│   ├── send-catering-emails.py         # Send catering emails
│   ├── slack-get-channel-ids.py        # Slack channel ID retriever
│   └── *.sh / *.py                     # Other utility scripts
│
├── 📁 pictures/                        # Documentation Images
│   ├── agent.jpg                       # AI agent screenshots
│   ├── agent_testing.jpg               # Testing screenshots
│   └── node_*.jpg                      # Workflow screenshots
│
├── 📄 Core Files
│   ├── main.py                         # Application entry point
│   ├── agent-config.json               # AI Assistant configuration
│   ├── requirements.txt                # Python dependencies
│   ├── Dockerfile                      # Container definition
│   ├── .env                           # Environment variables (not committed)
│   ├── CLAUDE.md                       # AI development guide
│   └── README.md                       # Main project documentation
```

## 🎯 Key Components

### Active Core Files
- **`main.py`**: Application entry point for Container Apps Jobs
- **`core/ai_assistant_openai_agent.py`**: Production AI Assistant with RAG
- **`agent-config.json`**: AI Assistant and Vector Store configuration
- **`deployments/documents/`**: Knowledge base files uploaded to Vector Store

### Active Scripts
- **`scripts/deployment/deploy-container-jobs.sh`**: Main production deployment
- **`scripts/testing/test-enhanced-rag-system.py`**: Comprehensive testing suite
- **`scripts/utilities/upload-files-rest-api.py`**: Vector Store file management

### Documentation
- **`docs/diagrams/`**: Comprehensive architecture and workflow diagrams
- **`README.md`**: Main project documentation with updated structure
- **`CLAUDE.md`**: Instructions for future AI development sessions

## 🔄 Migration from Old Structure

### What Was Moved
1. **Root scripts** → `scripts/{deployment,testing,utilities,archive}/`
2. **Documentation files** → `docs/`
3. **Unused/deprecated scripts** → `scripts/archive/`
4. **Test results** → `scripts/testing/`

### What Was Cleaned
- Removed `path/` directory (empty venv reference)
- Removed `monitoring/` directory (unused)
- Removed `rag-processing-log.txt` (temporary file)
- Archived multiple unused scripts and temporary files

### Legacy Components (Archived)
- **Logic Apps workflows**: Moved to `deployments/logic-apps/` (superseded by Container Apps Jobs)
- **Old AI implementations**: Kept in `core/` for reference but not used
- **Multiple deployment attempts**: Archived in `scripts/archive/`

## 🚀 Current Production Setup

### Active Architecture
- **Container Apps Jobs**: Scheduled email processing
- **Azure OpenAI Assistant**: AI Assistant `asst_UHTUDffJEyLQ6qexElqOopac`
- **Vector Store**: `vs_xDbEaqnBNUtJ70P7GoNgY1qD` with 6 knowledge documents
- **Cost Optimized**: $60-96/month (48% reduction)

### Key Scripts to Use
```bash
# Deploy production system
./scripts/deployment/deploy-container-jobs.sh

# Test the enhanced RAG system
python scripts/testing/test-enhanced-rag-system.py

# Upload knowledge files
python scripts/utilities/upload-files-rest-api.py

# Verify uploads
python scripts/utilities/verify-knowledge-upload.py
```

## 📊 Benefits of New Structure

1. **🎯 Clear Organization**: Scripts grouped by purpose
2. **🔍 Easy Navigation**: Logical directory structure
3. **📚 Better Documentation**: Centralized in `docs/`
4. **🗂️ Archive Management**: Deprecated files preserved but organized
5. **🚀 Faster Development**: Clear separation of active vs legacy code
6. **📈 Maintainability**: Easier to find and update components

## 🔮 Future Enhancements

The organized structure supports:
- **Modular Development**: Easy to add new features
- **Testing Framework**: Organized test suites
- **Documentation Growth**: Expandable docs structure
- **CI/CD Integration**: Clear deployment scripts
- **Team Collaboration**: Intuitive file organization