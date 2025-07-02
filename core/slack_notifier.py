"""
Enhanced Slack notifier for Jasmin Catering with full response text
"""

import requests
import json
from datetime import datetime
from typing import Dict, Optional, Any
from config.settings import SLACK_CONFIG


class SlackNotifier:
    """Handle Slack notifications with full message content"""
    
    def __init__(self):
        self.token = SLACK_CONFIG['bot_token']
        self.email_channel = SLACK_CONFIG['email_channel_id']
        self.log_channel = SLACK_CONFIG['log_channel_id']
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def post_email_request(self, email_data: Dict[str, Any]) -> bool:
        """Post incoming email to Slack"""
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "📧 New Catering Inquiry"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*From:* {email_data.get('from', 'Unknown')}"},
                    {"type": "mrkdwn", "text": f"*Subject:* {email_data['subject']}"},
                    {"type": "mrkdwn", "text": f"*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"},
                    {"type": "mrkdwn", "text": f"*ID:* {email_data.get('id', 'N/A')}"}
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Message:*\n```{email_data['body'][:500]}...```"
                }
            }
        ]
        
        return self._post_message(self.email_channel, "📧 New Catering Inquiry", blocks)
    
    def post_ai_response(self, email_subject: str, response_info: Dict[str, Any], 
                        full_response_text: str = None) -> bool:
        """Post AI response to Slack with full response text"""
        
        # Main response info
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🤖 AI Response Generated"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Subject:* Re: {email_subject}"},
                    {"type": "mrkdwn", "text": f"*Processing Time:* {response_info.get('processing_time', 'N/A')}"},
                    {"type": "mrkdwn", "text": f"*Documents Used:* {response_info.get('documents_used', 0)}"},
                    {"type": "mrkdwn", "text": f"*Status:* ✅ Sent"}
                ]
            }
        ]
        
        # Add pricing if available
        if response_info.get('pricing'):
            pricing_text = "\n".join([f"• {pkg}: {price}" for pkg, price in response_info['pricing'].items()])
            if pricing_text.strip():  # Only add if there's actual pricing
                blocks.append({
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Pricing Offered:*\n{pricing_text}"}
                })
        
        # Add full response text if provided
        if full_response_text:
            # Split long responses into chunks (Slack has a 3000 char limit per block)
            response_chunks = self._split_text(full_response_text, 2800)
            
            for i, chunk in enumerate(response_chunks):
                if i == 0:
                    blocks.append({
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"*Full AI Response:*\n```{chunk}```"}
                    })
                else:
                    blocks.append({
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"```{chunk}```"}
                    })
        
        # Add error message if response is missing
        elif 'error' in response_info:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*❌ Error:* {response_info['error']}"
                }
            })
        
        return self._post_message(self.email_channel, "🤖 AI Response Generated", blocks)
    
    def log(self, message: str, level: str = "info", details: Optional[Dict] = None) -> bool:
        """Send log message to log channel"""
        emoji = {"info": "ℹ️", "success": "✅", "error": "❌", "warning": "⚠️"}.get(level, "📌")
        
        blocks = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"{emoji} *{message}*"}
            }
        ]
        
        if details:
            details_text = json.dumps(details, indent=2, ensure_ascii=False)
            # Split large details into chunks
            details_chunks = self._split_text(details_text, 2800)
            
            for chunk in details_chunks:
                blocks.append({
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"```{chunk}```"}
                })
        
        return self._post_message(self.log_channel, message, blocks)
    
    def _split_text(self, text: str, max_length: int) -> list:
        """Split text into chunks that fit Slack's limits"""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        for line in text.split('\n'):
            if len(current_chunk) + len(line) + 1 <= max_length:
                current_chunk += line + '\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.rstrip())
                current_chunk = line + '\n'
        
        if current_chunk:
            chunks.append(current_chunk.rstrip())
        
        return chunks
    
    def _post_message(self, channel: str, text: str, blocks: list) -> bool:
        """Post message to Slack channel"""
        try:
            response = requests.post(
                'https://slack.com/api/chat.postMessage',
                headers=self.headers,
                json={'channel': channel, 'text': text, 'blocks': blocks}
            )
            result = response.json()
            
            if not result.get('ok'):
                print(f"Slack API error: {result.get('error', 'Unknown error')}")
                return False
                
            return True
        except Exception as e:
            print(f"Slack error: {e}")
            return False