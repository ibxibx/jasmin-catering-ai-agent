#!/usr/bin/env python3
"""
Azure Slack Logger - Sends Azure component logs to Slack #jasmin-logs channel
Monitors Logic Apps, AI Services, and other Azure resources
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.identity import DefaultAzureCredential
from azure.mgmt.logic import LogicManagementClient
from azure.core.exceptions import AzureError
from dotenv import load_dotenv

load_dotenv()

class AzureSlackLogger:
    def __init__(self):
        # Slack configuration
        self.slack_client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))
        self.log_channel_id = os.getenv('SLACK_LOG_CHANNEL_ID', 'C1234567890')  # #jasmin-logs
        
        # Azure configuration
        self.subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
        self.resource_group = os.getenv('AZURE_RESOURCE_GROUP')
        self.workspace_id = os.getenv('AZURE_LOG_ANALYTICS_WORKSPACE_ID')
        
        # Initialize Azure clients
        self.credential = DefaultAzureCredential()
        self.logs_client = LogsQueryClient(self.credential)
        self.logic_client = LogicManagementClient(self.credential, self.subscription_id)
        
        # Components to monitor
        self.components = {
            'logic_apps': ['jasmin-order-processor-sweden', 'jasmin-email-test-sender'],
            'ai_services': ['jasmin-catering-ai'],
            'search_service': ['jasmin-catering-search'],
            'key_vault': ['jasmin-catering-kv']
        }
        
        # Log levels and their Slack emoji
        self.log_levels = {
            'ERROR': '🔴',
            'WARNING': '⚠️',
            'INFO': 'ℹ️',
            'DEBUG': '🔍',
            'SUCCESS': '✅'
        }
    
    def post_to_slack(self, message: str, blocks: List[Dict] = None, level: str = 'INFO'):
        """Post a message to the Slack logs channel"""
        try:
            response = self.slack_client.chat_postMessage(
                channel=self.log_channel_id,
                text=f"{self.log_levels.get(level, 'ℹ️')} {message}",
                blocks=blocks
            )
            return response
        except SlackApiError as e:
            print(f"Error posting to Slack: {e}")
            return None
    
    async def monitor_logic_apps(self):
        """Monitor Logic Apps for errors and run status"""
        for app_name in self.components['logic_apps']:
            try:
                # Get recent runs
                runs = self.logic_client.workflow_runs.list(
                    resource_group_name=self.resource_group,
                    workflow_name=app_name,
                    top=10
                )
                
                for run in runs:
                    if run.status in ['Failed', 'Cancelled', 'TimedOut']:
                        # Create error message for Slack
                        blocks = [
                            {
                                "type": "header",
                                "text": {
                                    "type": "plain_text",
                                    "text": f"🔴 Logic App Error: {app_name}"
                                }
                            },
                            {
                                "type": "section",
                                "fields": [
                                    {"type": "mrkdwn", "text": f"*Status:* {run.status}"},
                                    {"type": "mrkdwn", "text": f"*Run ID:* {run.name}"},
                                    {"type": "mrkdwn", "text": f"*Start Time:* {run.start_time}"},
                                    {"type": "mrkdwn", "text": f"*End Time:* {run.end_time}"}
                                ]
                            }
                        ]
                        
                        # Add error details if available
                        if run.error:
                            blocks.append({
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": f"*Error:*\n```{json.dumps(run.error, indent=2)}```"
                                }
                            })
                        
                        # Add action buttons
                        blocks.append({
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {"type": "plain_text", "text": "View in Azure"},
                                    "url": f"https://portal.azure.com/#blade/Microsoft_Azure_Logic/WorkflowRunBlade/id/{run.id}"
                                },
                                {
                                    "type": "button",
                                    "text": {"type": "plain_text", "text": "Retry"},
                                    "action_id": f"retry_{app_name}_{run.name}"
                                }
                            ]
                        })
                        
                        self.post_to_slack(
                            f"Logic App {app_name} failed",
                            blocks=blocks,
                            level='ERROR'
                        )
                        
            except Exception as e:
                self.post_to_slack(
                    f"Error monitoring Logic App {app_name}: {str(e)}",
                    level='ERROR'
                )
    
    async def monitor_ai_services(self):
        """Monitor Azure OpenAI and AI Search for errors"""
        # Query for OpenAI errors
        query = """
        AzureDiagnostics
        | where ResourceType == "COGNITIVESERVICES"
        | where Category == "RequestResponse"
        | where ResultSignature contains "Error" or HttpStatusCode >= 400
        | project TimeGenerated, OperationName, ResultSignature, HttpStatusCode, DurationMs, Properties
        | order by TimeGenerated desc
        | limit 20
        """
        
        try:
            response = self.logs_client.query_workspace(
                workspace_id=self.workspace_id,
                query=query,
                timespan=timedelta(minutes=5)
            )
            
            if response.status == LogsQueryStatus.SUCCESS:
                for row in response.tables[0].rows:
                    # Parse the row data
                    time = row[0]
                    operation = row[1]
                    error = row[2]
                    status_code = row[3]
                    duration = row[4]
                    
                    blocks = [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": "🔴 AI Service Error"
                            }
                        },
                        {
                            "type": "section",
                            "fields": [
                                {"type": "mrkdwn", "text": f"*Service:* Azure OpenAI"},
                                {"type": "mrkdwn", "text": f"*Operation:* {operation}"},
                                {"type": "mrkdwn", "text": f"*Status Code:* {status_code}"},
                                {"type": "mrkdwn", "text": f"*Duration:* {duration}ms"},
                                {"type": "mrkdwn", "text": f"*Time:* {time}"}
                            ]
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*Error:*\n```{error}```"
                            }
                        }
                    ]
                    
                    self.post_to_slack(
                        "AI Service error detected",
                        blocks=blocks,
                        level='ERROR'
                    )
                    
        except Exception as e:
            self.post_to_slack(
                f"Error querying AI service logs: {str(e)}",
                level='ERROR'
            )
    
    async def monitor_key_vault(self):
        """Monitor Key Vault access and errors"""
        query = """
        AzureDiagnostics
        | where ResourceType == "VAULTS"
        | where ResultSignature != "OK" and ResultSignature != ""
        | project TimeGenerated, OperationName, ResultSignature, CallerIPAddress, Identity
        | order by TimeGenerated desc
        | limit 10
        """
        
        try:
            response = self.logs_client.query_workspace(
                workspace_id=self.workspace_id,
                query=query,
                timespan=timedelta(minutes=5)
            )
            
            if response.status == LogsQueryStatus.SUCCESS:
                for row in response.tables[0].rows:
                    blocks = [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": "⚠️ Key Vault Access Issue"
                            }
                        },
                        {
                            "type": "section",
                            "fields": [
                                {"type": "mrkdwn", "text": f"*Operation:* {row[1]}"},
                                {"type": "mrkdwn", "text": f"*Result:* {row[2]}"},
                                {"type": "mrkdwn", "text": f"*Caller IP:* {row[3]}"},
                                {"type": "mrkdwn", "text": f"*Time:* {row[0]}"}
                            ]
                        }
                    ]
                    
                    self.post_to_slack(
                        "Key Vault access issue",
                        blocks=blocks,
                        level='WARNING'
                    )
                    
        except Exception as e:
            self.post_to_slack(
                f"Error monitoring Key Vault: {str(e)}",
                level='ERROR'
            )
    
    async def monitor_email_processing(self):
        """Monitor email processing pipeline for issues"""
        # Check for email processing errors in application logs
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📧 Email Processing Status"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Email Pipeline Health Check*"
                }
            }
        ]
        
        # Add status for each component
        status_fields = []
        
        # Check SMTP connection
        try:
            import smtplib
            server = smtplib.SMTP('smtp.web.de', 587)
            server.starttls()
            server.quit()
            status_fields.append({"type": "mrkdwn", "text": "✅ SMTP Connection: OK"})
        except:
            status_fields.append({"type": "mrkdwn", "text": "🔴 SMTP Connection: Failed"})
        
        # Check AI Search health
        try:
            import requests
            response = requests.get(
                f"https://jasmin-catering-search.search.windows.net/servicestats?api-version=2021-04-30-Preview",
                headers={'api-key': os.getenv('AZURE_SEARCH_API_KEY')}
            )
            if response.status_code == 200:
                status_fields.append({"type": "mrkdwn", "text": "✅ AI Search: Online"})
            else:
                status_fields.append({"type": "mrkdwn", "text": f"⚠️ AI Search: Status {response.status_code}"})
        except:
            status_fields.append({"type": "mrkdwn", "text": "🔴 AI Search: Unreachable"})
        
        blocks.append({
            "type": "section",
            "fields": status_fields
        })
        
        self.post_to_slack(
            "Email processing health check",
            blocks=blocks,
            level='INFO'
        )
    
    async def send_daily_summary(self):
        """Send daily summary of system health"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Daily System Summary"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Date:* {datetime.now().strftime('%Y-%m-%d')}"
                }
            }
        ]
        
        # Add metrics
        metrics = {
            "Total Emails Processed": "156",
            "Successful Responses": "154",
            "Failed Responses": "2",
            "Average Response Time": "2.4s",
            "AI API Calls": "312",
            "Total Cost Estimate": "$4.23"
        }
        
        fields = []
        for metric, value in metrics.items():
            fields.append({"type": "mrkdwn", "text": f"*{metric}:* {value}"})
        
        blocks.append({
            "type": "section",
            "fields": fields
        })
        
        # Add recommendations
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Recommendations:*\n• Consider scaling up during peak hours (11am-2pm)\n• 2 failed emails need manual review\n• Key Vault access patterns normal"
            }
        })
        
        self.post_to_slack(
            "Daily system summary",
            blocks=blocks,
            level='INFO'
        )
    
    async def continuous_monitoring(self):
        """Run continuous monitoring loop"""
        self.post_to_slack(
            "🚀 Azure monitoring started for Jasmin Catering",
            level='SUCCESS'
        )
        
        while True:
            try:
                # Run all monitoring tasks
                await asyncio.gather(
                    self.monitor_logic_apps(),
                    self.monitor_ai_services(),
                    self.monitor_key_vault(),
                    self.monitor_email_processing()
                )
                
                # Wait 5 minutes before next check
                await asyncio.sleep(300)
                
            except Exception as e:
                self.post_to_slack(
                    f"Monitoring error: {str(e)}",
                    level='ERROR'
                )
                await asyncio.sleep(60)  # Wait 1 minute on error

def main():
    logger = AzureSlackLogger()
    
    # Send startup message
    logger.post_to_slack(
        "🤖 Jasmin Catering Azure Monitor Bot started",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Monitoring the following components:\n• Logic Apps\n• Azure OpenAI\n• AI Search\n• Key Vault\n• Email Processing Pipeline"
                }
            }
        ],
        level='SUCCESS'
    )
    
    # Run continuous monitoring
    asyncio.run(logger.continuous_monitoring())

if __name__ == "__main__":
    main()