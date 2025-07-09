#!/usr/bin/env python3
"""
Deep investigation of email inbox to find our test email
"""

import imaplib
import email
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def investigate_inbox():
    """Thoroughly investigate the email inbox"""
    
    imap_server = "imap.web.de"
    imap_port = 993
    email_address = os.getenv('FROM_EMAIL_ADDRESS', 'matthias.buchhorn@web.de')
    password = os.getenv('WEBDE_APP_PASSWORD')
    alias = os.getenv('WEBDE_EMAIL_ALIAS', 'ma3u-test@email.de')
    
    print(f"🔍 Deep Investigation of Email Inbox")
    print(f"=" * 50)
    print(f"📧 Login: {email_address}")
    print(f"🏷️  Target alias: {alias}")
    print(f"⏰ Current time: {datetime.now()}")
    print(f"📅 UTC time: {datetime.utcnow()}")
    
    try:
        # Connect to IMAP
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(email_address, password)
        
        # List all folders
        print(f"\n📁 Available folders:")
        folders = mail.list()
        for folder in folders[1]:
            print(f"  {folder.decode()}")
        
        mail.select('inbox')
        
        # Get total email count
        status, total = mail.search(None, 'ALL')
        total_count = len(total[0].split()) if total[0] else 0
        print(f"\n📊 Total emails in inbox: {total_count}")
        
        # Search for our test email specifically by subject
        print(f"\n🎯 Searching for our test email...")
        
        searches = [
            ("Test email by subject", 'SUBJECT "Test Catering Anfrage"'),
            ("Test email by time today", f'SINCE "{datetime.now().strftime("%d-%b-%Y")}"'),
            ("All emails to alias", f'TO "{alias}"'),
            ("Recent emails (last 2 hours)", f'SINCE "{(datetime.now() - timedelta(hours=2)).strftime("%d-%b-%Y")}"'),
        ]
        
        for search_name, search_query in searches:
            print(f"\n🔍 {search_name}: {search_query}")
            status, messages = mail.search(None, search_query)
            
            if status == 'OK' and messages[0]:
                email_ids = messages[0].split()
                print(f"📊 Found {len(email_ids)} emails")
                
                # Check each email in detail
                for email_id in email_ids[-5:]:  # Last 5 emails
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    if status == 'OK':
                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body)
                        
                        subject = email_message['Subject']
                        to_addr = email_message['To']
                        from_addr = email_message['From']
                        date = email_message['Date']
                        message_id = email_message['Message-ID']
                        
                        print(f"\n  📧 Email ID: {email_id.decode()}")
                        print(f"  📅 Date: {date}")
                        print(f"  👤 From: {from_addr}")
                        print(f"  📬 To: {to_addr}")
                        print(f"  📋 Subject: {subject}")
                        print(f"  🆔 Message-ID: {message_id}")
                        
                        # Check if this looks like our test email
                        if subject and "Test Catering Anfrage" in str(subject):
                            print(f"  🎯 THIS IS OUR TEST EMAIL!")
                            
                            # Get the body to check content
                            if email_message.is_multipart():
                                for part in email_message.walk():
                                    if part.get_content_type() == "text/plain":
                                        body = part.get_payload(decode=True).decode()
                                        break
                            else:
                                body = email_message.get_payload(decode=True).decode()
                            
                            print(f"  📄 Body preview: {body[:200]}...")
                            
                            # Check why Container Apps might miss this
                            print(f"\n  🔍 Analysis for Container Apps:")
                            print(f"    - Email ID: {email_id.decode()}")
                            print(f"    - To field matches alias: {alias in str(to_addr)}")
                            print(f"    - Contains 'catering': {'catering' in str(subject).lower()}")
                            print(f"    - Contains 'hochzeit': {'hochzeit' in str(subject).lower()}")
                            print(f"    - Date today: {datetime.now().strftime('%d-%b-%Y') in str(date)}")
                            
                        elif alias in str(to_addr):
                            print(f"  ✅ Email to our alias")
                        else:
                            print(f"  ❌ Not to our alias")
            else:
                print(f"❌ Search failed or no results: {status}")
        
        # Final check: Look for emails from the exact time we sent the test
        print(f"\n🕐 Looking for emails around 17:05:09 (15:05:09 UTC)...")
        # Search for emails in a wider time range
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
        status, messages = mail.search(None, f'SINCE "{yesterday}"')
        
        if status == 'OK' and messages[0]:
            email_ids = messages[0].split()
            print(f"📊 Found {len(email_ids)} emails since yesterday")
            
            # Look specifically for our test email
            found_test_email = False
            for email_id in email_ids:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status == 'OK':
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    subject = str(email_message['Subject'])
                    if "17:05:08" in subject or "Test Catering Anfrage" in subject:
                        found_test_email = True
                        print(f"\n🎯 FOUND OUR TEST EMAIL!")
                        print(f"  📧 ID: {email_id.decode()}")
                        print(f"  📋 Subject: {subject}")
                        print(f"  📬 To: {email_message['To']}")
                        print(f"  📅 Date: {email_message['Date']}")
                        break
            
            if not found_test_email:
                print(f"❌ Our test email not found in recent emails")
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"❌ Investigation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_inbox()