#!/usr/bin/env python3
"""
Get Slack Channel IDs for #email-requests-and-response and #jasmin-logs
"""

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

def get_channel_ids():
    """Get channel IDs for the required channels"""
    
    bot_token = os.getenv('SLACK_BOT_TOKEN')
    
    if not bot_token:
        print("❌ SLACK_BOT_TOKEN not found in .env")
        print("   Please complete OAuth setup first using: python slack-oauth-setup.py")
        return
    
    client = WebClient(token=bot_token)
    
    print("🔍 Searching for Slack channels...")
    print()
    
    channels_to_find = {
        'email-requests-and-response': None,
        'jasmin-logs': None
    }
    
    try:
        # Get all public channels
        response = client.conversations_list(
            types="public_channel",
            limit=200
        )
        
        if response['ok']:
            for channel in response['channels']:
                channel_name = channel['name']
                if channel_name in channels_to_find:
                    channels_to_find[channel_name] = channel['id']
                    print(f"✅ Found #{channel_name}: {channel['id']}")
            
            print()
            
            # Check which channels were not found
            not_found = [name for name, id in channels_to_find.items() if id is None]
            
            if not_found:
                print("⚠️  The following channels were not found:")
                for channel_name in not_found:
                    print(f"   - #{channel_name}")
                print()
                print("Please create these channels in Slack first, or invite the bot to private channels.")
            
            # Generate .env update
            if channels_to_find['email-requests-and-response']:
                print()
                print("📋 Add these to your .env file:")
                print(f'SLACK_CHANNEL_ID="{channels_to_find["email-requests-and-response"]}"')
                if channels_to_find['jasmin-logs']:
                    print(f'SLACK_LOG_CHANNEL_ID="{channels_to_find["jasmin-logs"]}"')
                
                # Also show Azure Key Vault commands
                print()
                print("🔐 Store in Azure Key Vault:")
                print(f'az keyvault secret set --vault-name "jasmin-catering-kv" --name "slack-channel-id" --value "{channels_to_find["email-requests-and-response"]}"')
                if channels_to_find['jasmin-logs']:
                    print(f'az keyvault secret set --vault-name "jasmin-catering-kv" --name "slack-log-channel-id" --value "{channels_to_find["jasmin-logs"]}"')
            
        else:
            print(f"❌ Error: {response['error']}")
            
    except SlackApiError as e:
        print(f"❌ Slack API Error: {e.response['error']}")
        
        if e.response['error'] == 'missing_scope':
            print()
            print("The bot needs the 'channels:read' scope.")
            print("Please reinstall the app with the correct scopes.")

def test_posting():
    """Test posting a message to the channels"""
    
    bot_token = os.getenv('SLACK_BOT_TOKEN')
    channel_id = os.getenv('SLACK_CHANNEL_ID')
    log_channel_id = os.getenv('SLACK_LOG_CHANNEL_ID')
    
    if not bot_token:
        print("❌ SLACK_BOT_TOKEN not found")
        return
    
    client = WebClient(token=bot_token)
    
    print()
    print("🧪 Testing message posting...")
    print()
    
    # Test email channel
    if channel_id:
        try:
            response = client.chat_postMessage(
                channel=channel_id,
                text="🤖 Jasmin Catering AI Agent connected to #email-requests-and-response!",
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "✅ *Connection Test Successful*\n\nThe Jasmin Catering AI Agent is now connected and will post:\n• Incoming catering inquiries\n• AI-generated responses\n• Processing status updates"
                        }
                    }
                ]
            )
            print("✅ Successfully posted to #email-requests-and-response")
        except SlackApiError as e:
            print(f"❌ Failed to post to email channel: {e.response['error']}")
    
    # Test log channel
    if log_channel_id:
        try:
            response = client.chat_postMessage(
                channel=log_channel_id,
                text="🤖 Jasmin Catering monitoring system connected!",
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "✅ *Monitoring System Connected*\n\nThe following will be logged here:\n• Azure service errors\n• Email processing issues\n• Performance metrics\n• Daily summaries"
                        }
                    }
                ]
            )
            print("✅ Successfully posted to #jasmin-logs")
        except SlackApiError as e:
            print(f"❌ Failed to post to log channel: {e.response['error']}")

def main():
    print("🚀 Slack Channel ID Finder")
    print("=" * 50)
    
    # Get channel IDs
    get_channel_ids()
    
    # Ask if user wants to test
    print()
    test = input("Would you like to test posting messages? (y/n): ").lower()
    
    if test == 'y':
        test_posting()

if __name__ == "__main__":
    main()