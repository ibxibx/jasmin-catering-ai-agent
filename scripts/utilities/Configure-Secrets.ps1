# PowerShell script to configure secrets in .env file
# Configure-Secrets.ps1

Write-Host "🔐 Jasmin Catering AI - Secret Configuration Helper" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

$EnvFile = ".env"

# Check if .env file exists
if (-not (Test-Path $EnvFile)) {
    Write-Host "❌ Error: .env file not found. Please run this from the project root directory." -ForegroundColor Red
    exit 1
}

Write-Host "This script will help you configure the required secrets in your .env file."
Write-Host "Press Enter to continue, or Ctrl+C to exit."
Read-Host

# Function to update .env file
function Update-EnvVar {
    param(
        [string]$VarName,
        [string]$VarValue
    )
    
    $content = Get-Content $EnvFile
    $updated = $false
    
    for ($i = 0; $i -lt $content.Length; $i++) {
        if ($content[$i] -match "^$VarName=") {
            $content[$i] = "$VarName=$VarValue"
            $updated = $true
            break
        }
    }
    
    if (-not $updated) {
        $content += "$VarName=$VarValue"
    }
    
    Set-Content -Path $EnvFile -Value $content
}

# Configure Web.de App Password
Write-Host ""
Write-Host "📧 Web.de Email Configuration" -ForegroundColor Yellow
Write-Host "============================="
Write-Host "Please enter your Web.de app password (not your regular password!):"
Write-Host "Format: abcd-efgh-ijkl-mnop"
$webdePassword = Read-Host "WEBDE_APP_PASSWORD"

if ($webdePassword) {
    Update-EnvVar "WEBDE_APP_PASSWORD" $webdePassword
    Write-Host "✅ Web.de app password configured" -ForegroundColor Green
} else {
    Write-Host "❌ Skipping Web.de configuration (empty password)" -ForegroundColor Red
}

# Configure Slack Bot Token
Write-Host ""
Write-Host "🔔 Slack Bot Token Configuration" -ForegroundColor Yellow
Write-Host "================================"
Write-Host "Please enter your Slack bot token:"
Write-Host "Format: xoxb-YOUR-BOT-TOKEN-HERE"
$slackToken = Read-Host "SLACK_BOT_TOKEN"

if ($slackToken) {
    Update-EnvVar "SLACK_BOT_TOKEN" $slackToken
    Write-Host "✅ Slack bot token configured" -ForegroundColor Green
} else {
    Write-Host "❌ Skipping Slack bot token configuration (empty token)" -ForegroundColor Red
}

# Configure Slack Channel ID
Write-Host ""
Write-Host "📱 Slack Channel ID Configuration" -ForegroundColor Yellow
Write-Host "================================="
Write-Host "Please enter your Slack channel ID for email requests and responses:"
Write-Host "Format: C1234567890"
$slackChannel = Read-Host "SLACK_CHANNEL_ID"

if ($slackChannel) {
    Update-EnvVar "SLACK_CHANNEL_ID" $slackChannel
    Write-Host "✅ Slack channel ID configured" -ForegroundColor Green
} else {
    Write-Host "❌ Skipping Slack channel ID configuration (empty ID)" -ForegroundColor Red
}

# Configure Slack Log Channel ID
Write-Host ""
Write-Host "📝 Slack Log Channel ID Configuration" -ForegroundColor Yellow
Write-Host "====================================="
Write-Host "Please enter your Slack log channel ID:"
Write-Host "Format: C0987654321"
$slackLogChannel = Read-Host "SLACK_LOG_CHANNEL_ID"

if ($slackLogChannel) {
    Update-EnvVar "SLACK_LOG_CHANNEL_ID" $slackLogChannel
    Write-Host "✅ Slack log channel ID configured" -ForegroundColor Green
} else {
    Write-Host "❌ Skipping Slack log channel ID configuration (empty ID)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 Secret Configuration Complete!" -ForegroundColor Green
Write-Host "================================="
Write-Host "Your .env file has been updated with the provided secrets."
Write-Host ""
Write-Host "📋 Current .env status:" -ForegroundColor Yellow
Write-Host "======================"

# Show current .env file (masking sensitive values)
$content = Get-Content $EnvFile
foreach ($line in $content) {
    if ($line -match "^([A-Z_]+)=(.*)$") {
        $varName = $matches[1]
        $varValue = $matches[2]
        
        if ($varValue) {
            Write-Host "✅ $varName=***configured***" -ForegroundColor Green
        } else {
            Write-Host "❌ $varName=***MISSING***" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Yellow
Write-Host "=============="
Write-Host "1. Review the configuration above"
Write-Host "2. Run the deployment script: ./scripts/deployment/deploy-initial.sh"
Write-Host "3. Monitor the deployment progress"
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Cyan
Write-Host "- All secrets are stored securely in Azure Key Vault during deployment"
Write-Host "- The .env file is used only for initial configuration"
Write-Host "- Never commit the .env file to version control"