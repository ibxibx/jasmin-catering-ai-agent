#!/usr/bin/env python3
"""
Clear test emails from the inbox to stop the flood
"""

import imaplib
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def clear_test_emails():
    """Delete all test emails from today"""
    # Email configuration
    IMAP_SERVER = "imap.web.de"
    IMAP_PORT = 993
    EMAIL_ADDRESS = os.getenv('FROM_EMAIL_ADDRESS', 'matthias.buchhorn@web.de')
    PASSWORD = os.getenv('WEBDE_APP_PASSWORD')
    ALIAS = os.getenv('WEBDE_EMAIL_ALIAS', 'ma3u-test@email.de')
    
    if not PASSWORD:
        print("❌ WEBDE_APP_PASSWORD not found in environment")
        return
    
    try:
        # Connect to IMAP
        print(f"🔌 Connecting to {IMAP_SERVER}...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ADDRESS, PASSWORD)
        mail.select('inbox')
        
        # Search for today's emails TO the test alias
        today = datetime.now().strftime("%d-%b-%Y")
        search_query = f'(TO "{ALIAS}") (SINCE "{today}")'
        print(f"🔍 Searching for test emails: {search_query}")
        
        status, messages = mail.search(None, search_query)
        if status == 'OK':
            email_ids = messages[0].split()
            count = len(email_ids)
            
            if count == 0:
                print("✅ No test emails found")
                return
            
            print(f"📧 Found {count} test emails from today")
            
            # Ask for confirmation
            response = input(f"Delete all {count} test emails? (yes/no): ")
            if response.lower() != 'yes':
                print("❌ Cancelled")
                return
            
            # Mark emails for deletion
            for email_id in email_ids:
                mail.store(email_id, '+FLAGS', '\\Deleted')
            
            # Expunge to permanently delete
            mail.expunge()
            print(f"✅ Deleted {count} test emails")
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧹 Test Email Cleanup Tool")
    print("=" * 50)
    clear_test_emails()