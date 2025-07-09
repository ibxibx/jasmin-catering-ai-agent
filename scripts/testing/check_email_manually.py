#!/usr/bin/env python3
"""
Check if test email was received
"""

import imaplib
import email
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

def check_recent_emails():
    """Check for recent emails in the test inbox"""
    
    imap_server = "imap.web.de"
    imap_port = 993
    email_address = os.getenv('FROM_EMAIL_ADDRESS', 'matthias.buchhorn@web.de')
    password = os.getenv('WEBDE_APP_PASSWORD')
    alias = os.getenv('WEBDE_EMAIL_ALIAS', 'ma3u-test@email.de')
    
    if not password:
        print("❌ WEBDE_APP_PASSWORD not found")
        return
    
    try:
        print(f"📧 Connecting to IMAP server...")
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(email_address, password)
        mail.select('INBOX')
        
        # Search for recent emails in the last hour
        cutoff = (datetime.now() - timedelta(hours=1)).strftime('%d-%b-%Y')
        status, messages = mail.search(None, f'SINCE {cutoff}')
        
        if status != 'OK':
            print("❌ Failed to search emails")
            return
            
        email_ids = messages[0].split()
        print(f"📬 Found {len(email_ids)} emails since {cutoff}")
        
        if not email_ids:
            print("📭 No recent emails found")
            return
            
        # Check the most recent emails
        for email_id in email_ids[-5:]:  # Last 5 emails
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            subject = email_message['Subject']
            to_addr = email_message['To']
            from_addr = email_message['From']
            date = email_message['Date']
            
            print(f"\n📧 Email ID: {email_id.decode()}")
            print(f"📅 Date: {date}")
            print(f"👤 From: {from_addr}")
            print(f"📬 To: {to_addr}")
            print(f"📋 Subject: {subject}")
            
            # Check if this is sent to our test alias
            if alias in (to_addr or ''):
                print(f"✅ This email is addressed to our test alias: {alias}")
            else:
                print(f"ℹ️  This email is not for our test alias ({alias})")
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"❌ Error checking emails: {e}")

if __name__ == "__main__":
    check_recent_emails()