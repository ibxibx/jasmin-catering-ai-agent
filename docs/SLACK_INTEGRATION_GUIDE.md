# Slack Integration Setup Guide

## 🚀 Complete Setup Instructions

### Prerequisites
✅ Slack API credentials in `.env` file
✅ Python environment with required packages
✅ Azure CLI configured

### Step 1: Complete OAuth Setup

1. **Run the OAuth setup script:**
   ```bash
   python slack-oauth-setup.py
   ```

2. **Follow the prompts:**
   - Browser will open automatically
   - Click the generated OAuth URL
   - Select your Slack workspace
   - Click "Allow" to authorize the app
   - Copy the authorization code from the redirect URL

3. **Paste the code when prompted**
   - The script will exchange it for a bot token
   - Bot token will be saved to `.env` and Azure Key Vault

### Step 2: Create Slack Channels

In your Slack workspace, create these channels if they don't exist:

1. **#email-requests-and-response**
   - For incoming email requests and AI responses
   - Public channel recommended

2. **#jasmin-logs**
   - For system logs, errors, and debug information
   - Can be private channel

### Step 3: Get Channel IDs

```bash
python get-slack-channels.py
```

This script will:
- Find the channel IDs for both channels
- Save them to `.env` file
- Upload them to Azure Key Vault

### Step 4: Invite Bot to Channels

In each channel, type:
```
/invite @jasmin-catering-bot
```

### Step 5: Test Integration

```bash
python test-slack-integration.py
```

This will send test messages to both channels to verify everything works.

## 🔧 Environment Variables

After setup, your `.env` should have:
```env
SLACK_BOT_TOKEN="xoxb-..."
SLACK_CHANNEL_ID="C123456789"      # #email-requests-and-response
SLACK_LOG_CHANNEL_ID="C987654321"  # #jasmin-logs
```

## 🏃 Running the Full System

Once Slack is configured:

1. **Process emails with Slack logging:**
   ```bash
   python process-emails-with-rag-proof.py
   ```

2. **Monitor Azure services:**
   ```bash
   python azure-slack-logger.py
   ```

## 📊 What Gets Logged

### #email-requests-and-response
- Incoming email requests (subject, sender, preview)
- AI-generated responses (pricing, processing time)
- RAG documents used

### #jasmin-logs
- System startup/shutdown
- Azure service status
- API calls and response times
- Errors and exceptions
- Performance metrics

## 🚨 Troubleshooting

### Bot Token Issues
- Ensure OAuth flow completed successfully
- Check token starts with `xoxb-`
- Verify token in Azure Key Vault

### Channel Not Found
- Create channels in Slack first
- Ensure bot is invited to channels
- Channel names must match exactly

### Permission Errors
- Bot needs these scopes: chat:write, chat:write.public, channels:read
- Re-run OAuth if scopes are missing

## 🔐 Security Notes

- Bot token is stored in Azure Key Vault
- Never commit tokens to git
- Use channel IDs, not channel names in production
- Rotate tokens periodically

## 📚 Next Steps

1. Set up monitoring dashboard in Slack
2. Configure alerts for critical errors
3. Add custom emoji reactions for status
4. Create Slack commands for manual triggers