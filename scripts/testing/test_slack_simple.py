#!/usr/bin/env python3
"""
Simple Slack test
"""

import os
from dotenv import load_dotenv
from core.slack_notifier import SlackNotifier

load_dotenv()

def test_slack_simple():
    """Simple Slack test"""
    
    print("🔔 Testing Slack with simple message...")
    
    try:
        slack = SlackNotifier()
        
        # Send test log message
        result = slack.log("🧪 Local test from development machine", "info", {
            "test": True,
            "time": "17:15",
            "purpose": "Testing if Slack integration works"
        })
        
        if result:
            print("✅ Slack test message sent successfully!")
            print("📱 Check the #jasmin-logs channel in Slack")
        else:
            print("❌ Failed to send Slack message")
            
    except Exception as e:
        print(f"❌ Slack test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_slack_simple()