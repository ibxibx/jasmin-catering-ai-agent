#!/bin/bash
# ==============================================================================
# Script: monitor-container-job.sh
# Purpose: Monitor Container Apps Job executions and logs
# Type: Monitoring Script
#
# Description:
#   Monitors the Jasmin email processor Container Apps Job, showing:
#   - Recent job executions and their status
#   - Logs from specific executions
#   - Email processing activity
#
# Usage:
#   ./scripts/deployment/monitoring/monitor-container-job.sh [command] [options]
#
# Commands:
#   list        - List recent job executions (default)
#   logs <name> - Show logs for specific execution
#   latest      - Show logs from the latest execution
#   stats       - Show job statistics
#
# Examples:
#   ./scripts/deployment/monitoring/monitor-container-job.sh
#   ./scripts/deployment/monitoring/monitor-container-job.sh latest
#   ./scripts/deployment/monitoring/monitor-container-job.sh logs jasmin-email-processor-12345
# ==============================================================================

# Configuration
RESOURCE_GROUP="logicapp-jasmin-sweden_group"
JOB_NAME="jasmin-email-processor"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default command
COMMAND="${1:-list}"

case "$COMMAND" in
    "list")
        echo "📊 Recent Job Executions for $JOB_NAME"
        echo "=========================================="
        az containerapp job execution list \
            --name $JOB_NAME \
            --resource-group $RESOURCE_GROUP \
            --query "[0:10].{Name:name, Status:properties.status, StartTime:properties.startTime, EndTime:properties.endTime}" \
            -o table
        ;;
        
    "logs")
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Please provide execution name${NC}"
            echo "Usage: $0 logs <execution-name>"
            exit 1
        fi
        
        echo "📜 Logs for execution: $2"
        echo "=========================================="
        az containerapp job logs show \
            --name $JOB_NAME \
            --resource-group $RESOURCE_GROUP \
            --container jasmin-email-processor \
            --job-execution-name "$2"
        ;;
        
    "latest")
        echo "🔍 Finding latest execution..."
        LATEST=$(az containerapp job execution list \
            --name $JOB_NAME \
            --resource-group $RESOURCE_GROUP \
            --query "[0].name" -o tsv)
            
        if [ -z "$LATEST" ]; then
            echo -e "${RED}No executions found${NC}"
            exit 1
        fi
        
        echo "📜 Logs for latest execution: $LATEST"
        echo "=========================================="
        az containerapp job logs show \
            --name $JOB_NAME \
            --resource-group $RESOURCE_GROUP \
            --container jasmin-email-processor \
            --job-execution-name "$LATEST"
        ;;
        
    "stats")
        echo "📈 Job Statistics"
        echo "=========================================="
        
        # Get job configuration
        echo -e "\n${YELLOW}Configuration:${NC}"
        az containerapp job show \
            --name $JOB_NAME \
            --resource-group $RESOURCE_GROUP \
            --query "{Schedule:properties.configuration.scheduleTriggerConfig.cronExpression, Image:properties.template.containers[0].image, Status:properties.runningStatus}" \
            -o table
            
        # Get execution statistics
        echo -e "\n${YELLOW}Recent Execution Summary:${NC}"
        az containerapp job execution list \
            --name $JOB_NAME \
            --resource-group $RESOURCE_GROUP \
            --query "[0:20]" -o json | jq -r '
            {
                total: length,
                succeeded: [.[] | select(.properties.status == "Succeeded")] | length,
                failed: [.[] | select(.properties.status == "Failed")] | length,
                running: [.[] | select(.properties.status == "Running")] | length
            }'
        ;;
        
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        echo "Available commands: list, logs, latest, stats"
        exit 1
        ;;
esac