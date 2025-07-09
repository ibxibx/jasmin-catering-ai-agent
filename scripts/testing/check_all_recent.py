#!/usr/bin/env python3
"""
Check all recent emails to see if the new one arrived anywhere
"""

import imaplib
import email
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def check_all_recent():
    """Check all recent emails"""
    
    imap_server = "imap.web.de"
    imap_port = 993
    email_address = os.getenv('FROM_EMAIL_ADDRESS', 'matthias.buchhorn@web.de')
    password = os.getenv('WEBDE_APP_PASSWORD')
    alias = os.getenv('WEBDE_EMAIL_ALIAS', 'ma3u-test@email.de')
    
    print(f"📧 Checking ALL recent emails for: 'Hochzeitsfeier'")
    print(f"🕐 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Connect to IMAP
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(email_address, password)
        mail.select('inbox')
        
        # Search for emails in the last hour
        cutoff = (datetime.now() - timedelta(minutes=30)).strftime('%d-%b-%Y')
        status, messages = mail.search(None, f'SINCE "{cutoff}"')
        
        if status == 'OK':
            email_ids = messages[0].split()
            print(f"📊 Found {len(email_ids)} emails in last 30 minutes")
            
            # Check the most recent emails
            recent_emails = email_ids[-10:] if len(email_ids) > 10 else email_ids
            print(f"📊 Checking last {len(recent_emails)} emails: {recent_emails}")
            
            for email_id in recent_emails:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status == 'OK':
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    subject = email_message['Subject']
                    date = email_message['Date']
                    from_addr = email_message['From']
                    to_addr = email_message['To']
                    
                    # Decode subject if encoded
                    if subject:
                        try:
                            decoded = email.header.decode_header(subject)[0]
                            if decoded[1]:
                                subject = decoded[0].decode(decoded[1])
                            else:
                                subject = str(decoded[0])
                        except:
                            subject = str(subject)
                    
                    print(f"\n📧 Email ID: {email_id.decode()}")
                    print(f"📅 Date: {date}")
                    print(f"👤 From: {from_addr}")
                    print(f"📬 To: {to_addr}")
                    print(f"📋 Subject: {subject}")
                    
                    # Check for our keywords
                    if "Hochzeitsfeier" in str(subject):
                        print(f"🎯 CONTAINS 'Hochzeitsfeier'!")
                        if "16. August 2025" in str(subject):
                            print(f"🎯 THIS IS THE NEW TEST EMAIL!")
                        
                    if alias in str(to_addr):
                        print(f"✅ Sent to our alias: {alias}")
                    else:
                        print(f"ℹ️  Not sent to our alias")
                        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"❌ Error checking emails: {e}")

if __name__ == "__main__":
    check_all_recent()