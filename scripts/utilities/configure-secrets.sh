#!/bin/bash
# Helper script to configure secrets in .env file

echo "🔐 Jasmin Catering AI - Secret Configuration Helper"
echo "=================================================="

ENV_FILE=".env"

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: .env file not found. Please run this from the project root directory."
    exit 1
fi

echo "This script will help you configure the required secrets in your .env file."
echo "Press Enter to continue, or Ctrl+C to exit."
read

# Function to update .env file
update_env_var() {
    local var_name=$1
    local var_value=$2
    
    if grep -q "^${var_name}=" "$ENV_FILE"; then
        # Update existing variable
        sed -i "s|^${var_name}=.*|${var_name}=${var_value}|" "$ENV_FILE"
    else
        # Add new variable
        echo "${var_name}=${var_value}" >> "$ENV_FILE"
    fi
}

# Configure Web.de App Password
echo ""
echo "📧 Web.de Email Configuration"
echo "============================="
echo "Please enter your Web.de app password (not your regular password!):"
echo "Format: abcd-efgh-ijkl-mnop"
read -p "WEBDE_APP_PASSWORD: " webde_password

if [ ! -z "$webde_password" ]; then
    update_env_var "WEBDE_APP_PASSWORD" "$webde_password"
    echo "✅ Web.de app password configured"
else
    echo "❌ Skipping Web.de configuration (empty password)"
fi

# Configure Slack Bot Token
echo ""
echo "🔔 Slack Bot Token Configuration"
echo "================================"
echo "Please enter your Slack bot token:"
echo "Format: xoxb-YOUR-BOT-TOKEN-HERE"
read -p "SLACK_BOT_TOKEN: " slack_token

if [ ! -z "$slack_token" ]; then
    update_env_var "SLACK_BOT_TOKEN" "$slack_token"
    echo "✅ Slack bot token configured"
else
    echo "❌ Skipping Slack bot token configuration (empty token)"
fi

# Configure Slack Channel ID
echo ""
echo "📱 Slack Channel ID Configuration"
echo "================================="
echo "Please enter your Slack channel ID for email requests and responses:"
echo "Format: C1234567890"
read -p "SLACK_CHANNEL_ID: " slack_channel

if [ ! -z "$slack_channel" ]; then
    update_env_var "SLACK_CHANNEL_ID" "$slack_channel"
    echo "✅ Slack channel ID configured"
else
    echo "❌ Skipping Slack channel ID configuration (empty ID)"
fi

# Configure Slack Log Channel ID
echo ""
echo "📝 Slack Log Channel ID Configuration"
echo "====================================="
echo "Please enter your Slack log channel ID:"
echo "Format: C0987654321"
read -p "SLACK_LOG_CHANNEL_ID: " slack_log_channel

if [ ! -z "$slack_log_channel" ]; then
    update_env_var "SLACK_LOG_CHANNEL_ID" "$slack_log_channel"
    echo "✅ Slack log channel ID configured"
else
    echo "❌ Skipping Slack log channel ID configuration (empty ID)"
fi

echo ""
echo "🎉 Secret Configuration Complete!"
echo "================================="
echo "Your .env file has been updated with the provided secrets."
echo ""
echo "📋 Current .env status:"
echo "======================"

# Show current .env file (masking sensitive values)
while IFS= read -r line; do
    if [[ $line =~ ^[A-Z_]+= ]]; then
        var_name=$(echo "$line" | cut -d'=' -f1)
        var_value=$(echo "$line" | cut -d'=' -f2-)
        
        if [ ! -z "$var_value" ]; then
            echo "✅ $var_name=***configured***"
        else
            echo "❌ $var_name=***MISSING***"
        fi
    fi
done < "$ENV_FILE"

echo ""
echo "🚀 Next Steps:"
echo "=============="
echo "1. Review the configuration above"
echo "2. Run the deployment script: ./scripts/deployment/deploy-initial.sh"
echo "3. Monitor the deployment progress"
echo ""
echo "💡 Tips:"
echo "- All secrets are stored securely in Azure Key Vault during deployment"
echo "- The .env file is used only for initial configuration"
echo "- Never commit the .env file to version control"
