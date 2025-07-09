#!/usr/bin/env python3
"""
Slack Notifier Module for Jasmin Catering
Handles all Slack notifications for email processing and logging
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

class SlackNotifier:
    def __init__(self):
        self.client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))
        self.email_channel = os.getenv('SLACK_CHANNEL_ID', 'email-requests-and-response')
        self.log_channel = os.getenv('SLACK_LOG_CHANNEL_ID', 'jasmin-logs')
        
    def post_email_request(self, email_data: Dict[str, Any]) -> Optional[Dict]:
        """Post incoming email request to #email-requests-and-response"""
        try:
            response = self.client.chat_postMessage(
                channel=self.email_channel,
                text=f"📧 New Catering Inquiry from {email_data.get('from', 'Unknown')}",
                blocks=[
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "📧 New Catering Inquiry"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f"*From:* {email_data.get('from', 'Unknown')}"},
                            {"type": "mrkdwn", "text": f"*Subject:* {email_data.get('subject', 'No Subject')}"},
                            {"type": "mrkdwn", "text": f"*Time:* {email_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}"},
                            {"type": "mrkdwn", "text": f"*Email ID:* {email_data.get('id', 'N/A')}"}
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Message Preview:*\n```{email_data.get('body', '')[:500]}{'...' if len(email_data.get('body', '')) > 500 else ''}```"
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"📊 Message Length: {len(email_data.get('body', ''))} chars | 🏷️ Auto-categorized as: Catering Inquiry"
                            }
                        ]
                    }
                ]
            )
            return response
        except SlackApiError as e:
            self.log_error(f"Failed to post email request: {e}")
            return None
    
    def post_ai_response(self, response_data: Dict[str, Any]) -> Optional[Dict]:
        """Post AI-generated response to #email-requests-and-response"""
        try:
            # Extract pricing if available
            pricing_info = response_data.get('pricing', {})
            pricing_text = ""
            if pricing_info:
                pricing_text = "\n*Packages Offered:*\n"
                for package, price in pricing_info.items():
                    pricing_text += f"• {package}: {price}\n"
            
            response = self.client.chat_postMessage(
                channel=self.email_channel,
                text=f"🤖 AI Response Generated for {response_data.get('to', 'Unknown')}",
                blocks=[
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "🤖 AI Response Generated"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f"*To:* {response_data.get('to', 'Unknown')}"},
                            {"type": "mrkdwn", "text": f"*Subject:* Re: {response_data.get('subject', 'No Subject')}"},
                            {"type": "mrkdwn", "text": f"*Processing Time:* {response_data.get('processing_time', 'N/A')}"},
                            {"type": "mrkdwn", "text": f"*Response Length:* {len(response_data.get('response', ''))} chars"}
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Response Preview:*\n```{response_data.get('response', '')[:400]}...```"
                        }
                    }
                ]
            )
            
            # Add pricing section if available
            if pricing_text:
                self.client.chat_postMessage(
                    channel=self.email_channel,
                    thread_ts=response['ts'],
                    text=pricing_text
                )
            
            return response
        except SlackApiError as e:
            self.log_error(f"Failed to post AI response: {e}")
            return None
    
    def log_error(self, message: str, exception: Optional[Exception] = None, context: Optional[Dict] = None):
        """Log error to #jasmin-logs"""
        try:
            error_blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🔴 Error Detected"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Error:* {message}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"},
                        {"type": "mrkdwn", "text": f"*Component:* Email Processor"}
                    ]
                }
            ]
            
            if exception:
                error_blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Exception Type:* `{type(exception).__name__}`\n*Details:* ```{str(exception)}```"
                    }
                })
            
            if context:
                error_blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Context:*\n```{json.dumps(context, indent=2)}```"
                    }
                })
            
            self.client.chat_postMessage(
                channel=self.log_channel,
                text=f"🔴 Error: {message}",
                blocks=error_blocks
            )
        except SlackApiError as e:
            print(f"Failed to log error to Slack: {e}")
    
    def log_info(self, message: str, details: Optional[Dict] = None):
        """Log info message to #jasmin-logs"""
        try:
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"ℹ️ *INFO:* {message}"
                    }
                }
            ]
            
            if details:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"```{json.dumps(details, indent=2)}```"
                    }
                })
            
            self.client.chat_postMessage(
                channel=self.log_channel,
                text=f"ℹ️ {message}",
                blocks=blocks
            )
        except SlackApiError as e:
            print(f"Failed to log info to Slack: {e}")
    
    def log_success(self, message: str, metrics: Optional[Dict] = None):
        """Log success message to #jasmin-logs"""
        try:
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"✅ *SUCCESS:* {message}"
                    }
                }
            ]
            
            if metrics:
                fields = []
                for key, value in metrics.items():
                    fields.append({"type": "mrkdwn", "text": f"*{key}:* {value}"})
                
                blocks.append({
                    "type": "section",
                    "fields": fields[:8]  # Slack limits to 10 fields
                })
            
            self.client.chat_postMessage(
                channel=self.log_channel,
                text=f"✅ {message}",
                blocks=blocks
            )
        except SlackApiError as e:
            print(f"Failed to log success to Slack: {e}")
    
    def send_daily_summary(self, stats: Dict[str, Any]):
        """Send daily summary to #jasmin-logs"""
        try:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 Daily Summary Report"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Date:* {datetime.now().strftime('%A, %B %d, %Y')}"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Total Emails:* {stats.get('total_emails', 0)}"},
                        {"type": "mrkdwn", "text": f"*Processed:* {stats.get('processed', 0)}"},
                        {"type": "mrkdwn", "text": f"*Success Rate:* {stats.get('success_rate', '0%')}"},
                        {"type": "mrkdwn", "text": f"*Avg Response Time:* {stats.get('avg_response_time', 'N/A')}"},
                        {"type": "mrkdwn", "text": f"*AI API Calls:* {stats.get('api_calls', 0)}"},
                        {"type": "mrkdwn", "text": f"*Estimated Cost:* ${stats.get('estimated_cost', '0.00')}"}
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Top Inquiry Types:*\n{stats.get('top_inquiries', 'N/A')}"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "📈 View detailed analytics in Azure Portal | 🔍 Check #email-requests-and-response for all communications"
                        }
                    ]
                }
            ]
            
            self.client.chat_postMessage(
                channel=self.log_channel,
                text="📊 Daily Summary Report",
                blocks=blocks
            )
        except SlackApiError as e:
            print(f"Failed to send daily summary: {e}")

# Convenience functions for quick logging
def log_to_slack(message: str, level: str = "INFO", **kwargs):
    """Quick function to log to Slack"""
    notifier = SlackNotifier()
    
    if level == "ERROR":
        notifier.log_error(message, **kwargs)
    elif level == "SUCCESS":
        notifier.log_success(message, **kwargs)
    else:
        notifier.log_info(message, **kwargs)

if __name__ == "__main__":
    # Test the notifier
    notifier = SlackNotifier()
    
    # Test email notification
    test_email = {
        'from': 'test@example.com',
        'subject': 'Test Catering Inquiry',
        'body': 'This is a test email for Slack integration.',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    notifier.post_email_request(test_email)
    
    # Test response notification
    test_response = {
        'to': 'test@example.com',
        'subject': 'Test Catering Inquiry',
        'response': 'This is a test AI response.',
        'processing_time': '2.3s'
    }
    
    notifier.post_ai_response(test_response)
    
    # Test logging
    notifier.log_info("Slack notifier test completed")
    notifier.log_success("All tests passed", {'test_count': 3})
    notifier.log_error("This is a test error", Exception("Test exception"))