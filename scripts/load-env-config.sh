#!/bin/bash

# Load environment configuration for Jasmin Catering deployments
# Default deployment location: Sweden Central

# Load .env file from project root
ENV_FILE="$(dirname "$0")/../../.env"

if [ -f "$ENV_FILE" ]; then
    echo "Loading configuration from .env..."
    # Export only valid environment variables, skip comments
    set -a
    source <(grep -E '^[A-Z_]+=.*' "$ENV_FILE" | grep -v '^#')
    set +a
    echo "✅ Configuration loaded successfully"
else
    echo "❌ Error: .env file not found at $ENV_FILE"
    exit 1
fi

# Set default Azure location to Sweden Central
# This is required due to Azure region restrictions in West Europe
export AZURE_LOCATION="${AZURE_LOCATION:-swedencentral}"
echo "📍 Region: $AZURE_LOCATION (default: Sweden Central)"

# Display loaded configuration
echo "📋 Configuration Summary:"
echo "- Subscription: ${AZURE_SUBSCRIPTION_ID:0:8}..."
echo "- AI Service: Azure AI Foundry"
if [ ! -z "${WEBDE_EMAIL_ALIAS:-}" ]; then
    echo "- Email Filter: $WEBDE_EMAIL_ALIAS"
fi

# Validate required variables
required_vars=(
    "AZURE_SUBSCRIPTION_ID"
    "AZURE_RESOURCE_GROUP"
    "AZURE_AI_API_KEY"
    "WEBDE_EMAIL_ALIAS"
)

missing_vars=()
for var in "${required_vars[@]}"; do
    eval "value=\${$var:-}"
    if [ -z "$value" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Error: Missing required environment variables:"
    printf '  - %s\n' "${missing_vars[@]}"
    exit 1
fi

echo "✅ All required variables are set"