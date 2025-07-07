#!/usr/bin/env python3
"""
Test Slack integration
"""

import os
from dotenv import load_dotenv
from core.slack_notifier import SlackNotifier

load_dotenv()

def test_slack():
    """Test Slack notifications"""
    
    print("🔔 Testing Slack integration...")
    
    try:
        slack = SlackNotifier()
        
        # Send test notification
        result = slack.send_message(
            "🧪 Test from local development",
            "This is a test message to verify Slack integration is working."
        )
        
        if result:
            print("✅ Slack message sent successfully!")
        else:
            print("❌ Failed to send Slack message")
            
        # Send log message
        log_result = slack.log("Testing Slack integration", "info", {
            "test": True,
            "timestamp": "2025-07-07 17:15:00"
        })
        
        if log_result:
            print("✅ Slack log sent successfully!")
        else:
            print("❌ Failed to send Slack log")
            
    except Exception as e:
        print(f"❌ Slack test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_slack()