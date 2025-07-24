# PowerShell script for Jasmin Catering AI Email Processor Deployment
# Fixed version

# Helper function to load .env file
function Load-DotEnv {
    param([string]$Path)
    if (!(Test-Path $Path)) {
        Write-Error ".env file not found at $Path"
        exit 1
    }
    Get-Content $Path | ForEach-Object {
        if ($_ -match '^[A-Z_]+=.*' -and $_ -notmatch '^#') {
            $parts = $_ -split '=', 2
            $name = $parts[0].Trim()
            $value = $parts[1].Trim()
            [System.Environment]::SetEnvironmentVariable($name, $value)
        }
    }
}

# Load .env from project root
$envFile = Join-Path $PSScriptRoot "..\..\.env"
Load-DotEnv $envFile

# Required environment variables
$requiredVars = @(
    'AZURE_SUBSCRIPTION_ID',
    'AZURE_AI_API_KEY'
)
$missingVars = @()
foreach ($var in $requiredVars) {
    $value = [System.Environment]::GetEnvironmentVariable($var)
    if (-not $value) {
        $missingVars += $var
    }
}
if ($missingVars.Count -gt 0) {
    Write-Error "Missing required environment variables: $($missingVars -join ', ')"
    exit 1
}

# Set deployment variables
$AZURE_LOCATION = $env:AZURE_LOCATION
if (-not $AZURE_LOCATION) { $AZURE_LOCATION = 'swedencentral' }
$RESOURCE_GROUP = $env:AZURE_RESOURCE_GROUP
if (-not $RESOURCE_GROUP) { $RESOURCE_GROUP = 'logicapp-jasmin-sweden_group' }
$LOGIC_APP_NAME = $env:LOGIC_APP_NAME
if (-not $LOGIC_APP_NAME) { $LOGIC_APP_NAME = 'jasmin-order-processor-sweden' }

Write-Host "🚀 Jasmin Catering AI Email Processor Deployment"
Write-Host "==============================================="
Write-Host ""
Write-Host "📍 Configuration:"
Write-Host "- Region: $AZURE_LOCATION"Write-Host "- Resource Group: $RESOURCE_GROUP"
Write-Host "- Logic App: $LOGIC_APP_NAME"
Write-Host "- AI Service: Azure Cognitive Services (GPT-4)"
Write-Host ""

# Check Azure login
Write-Host "📝 Checking Azure login..."
$azAccount = az account show 2>$null
if (-not $azAccount) {
    Write-Host "Please login to Azure:"
    az login --use-device-code
}

# Set subscription
az account set --subscription $env:AZURE_SUBSCRIPTION_ID

# Create resource group
Write-Host ""
Write-Host "📁 Creating resource group..."
az group create --name $RESOURCE_GROUP --location $AZURE_LOCATION --output none | Out-Null

# Prepare workflow file
$workflowFile = Join-Path $PSScriptRoot "..\logic-apps\email-processor-workflow.json"
if (!(Test-Path $workflowFile)) {
    Write-Error "❌ Error: Workflow definition not found at $workflowFile"
    exit 1
}
# Inject API key into workflow
$tempWorkflow = "temp-workflow.json"
$workflowContent = Get-Content $workflowFile -Raw
$workflowContent = $workflowContent -replace '@\{parameters\(''apiKey''\)\}', $env:AZURE_AI_API_KEY
Set-Content -Path $tempWorkflow -Value $workflowContent

# Create or update Logic App
Write-Host ""
Write-Host "📱 Creating Logic App..."
$createResult = az logic workflow create --resource-group $RESOURCE_GROUP --name $LOGIC_APP_NAME --definition "@$tempWorkflow" --location $AZURE_LOCATION --output none 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Logic App exists, updating..."
    az logic workflow update --resource-group $RESOURCE_GROUP --name $LOGIC_APP_NAME --definition "@$tempWorkflow" --output none
}

# Clean up temp file
Remove-Item $tempWorkflow -ErrorAction SilentlyContinue

# Get deployment status
Write-Host ""
Write-Host "✅ Deployment Complete!"
Write-Host ""

$workflowState = az logic workflow show --resource-group $RESOURCE_GROUP --name $LOGIC_APP_NAME --query state -o tsv
Write-Host "📋 Deployment Summary:"
Write-Host "- Logic App: $LOGIC_APP_NAME"
Write-Host "- State: $workflowState"
Write-Host "- Resource Group: $RESOURCE_GROUP"
Write-Host "- Location: $AZURE_LOCATION"
Write-Host ""

# Show portal link
Write-Host "🔗 Azure Portal:"
Write-Host "https://portal.azure.com/#resource/subscriptions/$($env:AZURE_SUBSCRIPTION_ID)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Logic/workflows/$LOGIC_APP_NAME"
Write-Host ""

Write-Host "✨ Done! The email processor is deployed and ready."