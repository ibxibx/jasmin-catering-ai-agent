# Slack Integration Setup Guide

This guide will help you complete the Slack integration for Jasmin Catering AI Agent.

## 📋 Prerequisites

You already have:
- ✅ Slack App created with App ID: `A093MARMMRV`
- ✅ Client credentials stored in `.env`
- ✅ Channels created: `#email-requests-and-response` and `#jasmin-logs`

## 🚀 Step 1: Get Bot Token

### Option A: Using the Setup Script (Recommended)

```bash
# Run the OAuth setup script
python slack-oauth-setup.py
```

This will:
1. Open your browser with the OAuth URL
2. Ask you to authorize the app in your workspace
3. Give you a code to paste back
4. Exchange the code for a bot token

### Option B: Manual OAuth Flow

1. Visit this URL in your browser:
```
https://slack.com/oauth/v2/authorize?client_id=9106923844739.9123365735879&scope=chat:write+chat:write.public+channels:read+channels:history+files:write+users:read+team:read
```

2. Select your workspace and click "Allow"

3. Copy the `code` parameter from the redirect URL

4. Exchange the code for a token:
```bash
curl -X POST https://slack.com/api/oauth.v2.access \
  -d "client_id=9106923844739.9123365735879" \
  -d "client_secret=d7d11436cbcce524860d9d24a77357fa" \
  -d "code=YOUR_CODE_HERE"
```

5. Copy the `access_token` from the response (starts with `xoxb-`)

## 🔍 Step 2: Get Channel IDs

After adding the bot token to your `.env` file:

```bash
# Update .env with your bot token
SLACK_BOT_TOKEN="xoxb-your-bot-token-here"

# Run the channel ID finder
python slack-get-channel-ids.py
```

This will find your channels and give you the IDs to add to `.env`:
```bash
SLACK_CHANNEL_ID="C1234567890"  # #email-requests-and-response
SLACK_LOG_CHANNEL_ID="C0987654321"  # #jasmin-logs
```

## 🔐 Step 3: Store in Azure Key Vault

Store all Slack secrets in Azure Key Vault:

```bash
# Store bot token
az keyvault secret set \
  --vault-name "jasmin-catering-kv" \
  --name "slack-bot-token" \
  --value "xoxb-your-bot-token"

# Store channel IDs
az keyvault secret set \
  --vault-name "jasmin-catering-kv" \
  --name "slack-channel-id" \
  --value "C1234567890"

az keyvault secret set \
  --vault-name "jasmin-catering-kv" \
  --name "slack-log-channel-id" \
  --value "C0987654321"

# Store app credentials
az keyvault secret set \
  --vault-name "jasmin-catering-kv" \
  --name "slack-client-id" \
  --value "9106923844739.9123365735879"

az keyvault secret set \
  --vault-name "jasmin-catering-kv" \
  --name "slack-client-secret" \
  --value "d7d11436cbcce524860d9d24a77357fa"

az keyvault secret set \
  --vault-name "jasmin-catering-kv" \
  --name "slack-signing-secret" \
  --value "029722aed85ef7e54feffe6c21a0e2f4"
```

## 🧪 Step 4: Test the Integration

### Test Slack Posting

```bash
# Test the Slack notifier
python slack-notifier.py
```

This will send test messages to both channels.

### Test Email Processing with Slack

```bash
# Run email processor with Slack logging
python enhanced-email-processor-with-logging.py
```

## 📝 Step 5: Update Logic Apps

Add Slack webhook to your Logic Apps for error handling:

1. Go to Slack App settings > Incoming Webhooks
2. Enable Incoming Webhooks
3. Add New Webhook to Workspace
4. Select `#jasmin-logs` channel
5. Copy the webhook URL

Add to Logic App parameters:
```json
{
  "slackWebhookUrl": {
    "type": "String",
    "defaultValue": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  }
}
```

## ✅ Final .env Configuration

Your complete `.env` should have:

```bash
# Slack Configuration
SLACK_APP_ID="A093MARMMRV"
SLACK_CLIENT_ID="9106923844739.9123365735879"
SLACK_CLIENT_SECRET="d7d11436cbcce524860d9d24a77357fa"
SLACK_SIGNING_SECRET="029722aed85ef7e54feffe6c21a0e2f4"
SLACK_VERIFICATION_TOKEN="hm4WXEbcayYfXucovxqcNajo"
SLACK_BOT_TOKEN="xoxb-9106923844739-9124590351703-..."  # Your actual token
SLACK_CHANNEL_ID="C..."  # ID for #email-requests-and-response
SLACK_LOG_CHANNEL_ID="C..."  # ID for #jasmin-logs
```

## 🎯 What Happens Next

Once configured:

### In #email-requests-and-response:
- 📧 Every incoming catering email
- 🤖 Every AI-generated response
- 💰 Pricing summaries
- ⏱️ Processing times

### In #jasmin-logs:
- 🔴 All errors with stack traces
- ⚠️ Warnings and issues
- ℹ️ Debug information
- ✅ Success confirmations
- 📊 Daily summaries

## 🆘 Troubleshooting

### Bot can't post messages
- Ensure bot is in the channel (invite with `/invite @jasmin-catering-email-bot`)
- Check bot has `chat:write` scope
- Verify channel ID is correct

### OAuth fails
- Check client credentials are correct
- Ensure redirect URI matches app settings
- Try regenerating client secret

### Missing permissions
- Reinstall the app with all required scopes
- Check workspace admin hasn't restricted app installations

## 📚 Additional Resources

- [Slack API Documentation](https://api.slack.com/docs)
- [Bot Token Types](https://api.slack.com/authentication/token-types)
- [Block Kit Builder](https://app.slack.com/block-kit-builder) - Design message layouts
- [API Tester](https://api.slack.com/methods/chat.postMessage/test) - Test API calls