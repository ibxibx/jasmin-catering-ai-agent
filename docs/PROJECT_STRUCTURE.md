# 📁 Jasmin Catering AI Agent - Project Structure

## Optimized Directory Structure

```
jasmin-catering-ai-agent/
│
├── config/                     # Configuration management
│   └── settings.py            # Centralized settings
│
├── core/                      # Core application modules
│   ├── ai_assistant.py       # AI + RAG logic
│   ├── email_processor.py    # Email handling
│   └── slack_notifier.py     # Slack notifications
│
├── knowledge-base/            # Business knowledge for RAG
│   └── documents/
│       ├── business-info.md
│       ├── menu-offerings.md
│       ├── pricing-structure.md
│       └── service-policies.md
│
├── utils/                     # Utility scripts
│   └── send_test_emails.py   # Test email sender
│
├── docs/                      # Documentation
│   ├── README.md
│   ├── PRICING_EXPLANATION.md
│   ├── SLACK_INTEGRATION_GUIDE.md
│   └── RAG_PROOF_REPORT.md
│
├── .env                       # Environment variables
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
└── main.py                   # Main application entry point
```

## Key Improvements

### 1. **Centralized Configuration** (`config/settings.py`)
- All settings in one place
- Easy to modify and maintain
- Environment variables properly managed

### 2. **Modular Core Components** (`core/`)
- Clean separation of concerns
- Each module has a single responsibility
- Easy to test and maintain

### 3. **Simplified Dependencies**
- Removed duplicate email processors
- Consolidated AI assistant logic
- Unified Slack notification system

### 4. **Clean Utilities** (`utils/`)
- Only essential utility scripts
- Test email sender for easy testing

## Running the System

### 1. Send Test Emails
```bash
python utils/send_test_emails.py
```

### 2. Process Emails
```bash
python main.py
```

### 3. Check Results
- **Slack**: #email-requests-and-response and #jasmin-logs
- **Email**: Check inbox for responses

## Configuration

All configuration is in `config/settings.py`:
- Azure services
- Email settings
- Slack channels
- Business rules

## Benefits

1. **Maintainability**: Clear structure, easy to navigate
2. **Scalability**: Modular design allows easy extensions
3. **Performance**: No duplicate code or unnecessary files
4. **Clarity**: Each file has a clear purpose