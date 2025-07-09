# Jasmin Catering AI Agent - Script Organization Guide

## 📁 Script Directory Structure

```
scripts/deployment/
├── core/                    # Main deployment scripts
├── monitoring/              # System monitoring tools  
├── utilities/               # Helper and configuration scripts
└── fixes/                   # Documented temporary fixes
```

## 🚀 Core Deployment Scripts

### `core/deploy-container-jobs.sh`
- **Purpose**: Primary deployment script for Azure Container Apps Job
- **Type**: Core Deployment
- **Usage**: `./scripts/deployment/core/deploy-container-jobs.sh`
- **Function**: Builds Docker image, pushes to ACR, deploys/updates Container Apps Job

### `core/deploy-full-stack.sh`
- **Purpose**: Master orchestrator for complete system deployment
- **Type**: Core Deployment  
- **Usage**: `./scripts/deployment/core/deploy-full-stack.sh [--skip-build] [--dry-run]`
- **Function**: Validates environment, orchestrates deployment, verifies success

### `core/deploy-to-azure.sh`
- **Purpose**: Alternative deployment method using Azure CLI
- **Type**: Core Deployment
- **Usage**: Called by CI/CD or manually for deployment

## 📊 Monitoring Scripts

### `monitoring/monitor-container-job.sh`
- **Purpose**: Monitor Container Apps Job executions and logs
- **Type**: Monitoring
- **Usage**: 
  - `./scripts/deployment/monitoring/monitor-container-job.sh list`
  - `./scripts/deployment/monitoring/monitor-container-job.sh latest`
  - `./scripts/deployment/monitoring/monitor-container-job.sh logs <execution-name>`
  - `./scripts/deployment/monitoring/monitor-container-job.sh stats`

### `monitoring/show-email-responses.sh`
- **Purpose**: View email processing responses
- **Type**: Monitoring
- **Usage**: `./scripts/deployment/monitoring/show-email-responses.sh`

### `monitoring/show-corrected-emails.sh`
- **Purpose**: Display corrected email content
- **Type**: Monitoring
- **Usage**: `./scripts/deployment/monitoring/show-corrected-emails.sh`

## 🔧 Utility Scripts

### `utilities/load-env-config.sh`
- **Purpose**: Load environment variables from .env file
- **Type**: Utility
- **Usage**: `source scripts/deployment/utilities/load-env-config.sh`
- **Function**: Sources .env, validates required variables, sets defaults

### `utilities/setup-github-secrets.sh`
- **Purpose**: Configure GitHub Actions secrets
- **Type**: Utility
- **Usage**: `./scripts/deployment/utilities/setup-github-secrets.sh`

### `utilities/update-container-job-config.sh`
- **Purpose**: Update Container Apps Job configuration
- **Type**: Utility
- **Usage**: `./scripts/deployment/utilities/update-container-job-config.sh`

### `utilities/setup-email-tracking.sh`
- **Purpose**: Set up Azure Table Storage for email tracking
- **Type**: Utility
- **Usage**: `./scripts/deployment/utilities/setup-email-tracking.sh`

### `utilities/local-cicd.sh`
- **Purpose**: Local CI/CD deployment without GitHub Actions
- **Type**: Utility
- **Usage**: `./scripts/deployment/utilities/local-cicd.sh`

## 🔨 Fix Documentation Scripts

### `fixes/fix-duplicate-emails.sh`
- **Purpose**: Documents the duplicate email processing fix
- **Type**: Fix Documentation (Temporary)
- **Created**: 2025-07-09
- **Issue**: Emails were processed multiple times
- **Solution**: UNSEEN filter + mark as read implementation
- **Note**: Changes already integrated into codebase

## 📋 Script Naming Conventions

1. **Deployment scripts**: `deploy-*.sh`
2. **Monitoring scripts**: `monitor-*.sh` or `show-*.sh`
3. **Setup scripts**: `setup-*.sh`
4. **Update scripts**: `update-*.sh`
5. **Fix scripts**: `fix-*.sh`

## 🎯 Best Practices

1. **Always use proper headers**: Every script includes purpose, type, usage, and description
2. **Category placement**: Place scripts in appropriate subdirectories
3. **Documentation**: Document temporary fixes in the `fixes/` directory
4. **Executable permissions**: Ensure scripts have execute permissions (`chmod +x`)
5. **Error handling**: Use `set -e` for deployment scripts
6. **Color output**: Use color codes for better visibility in terminal

## 🔄 Migration Guide

If you're looking for old scripts:
- Check `scripts/archive/` for legacy scripts
- Python test scripts moved to `scripts/testing/`
- Old deployment scripts archived after consolidation

## 📝 Adding New Scripts

When creating new scripts:
1. Determine the category (core, monitoring, utilities, or fixes)
2. Use the standard header template
3. Place in appropriate subdirectory
4. Update this documentation
5. Make executable: `chmod +x script-name.sh`