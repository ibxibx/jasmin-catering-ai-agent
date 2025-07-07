#!/usr/bin/env python3
"""
Debug email fetching to see why emails aren't found
"""

import imaplib
import email
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def debug_email_fetch():
    """Debug email fetching process"""
    
    imap_server = "imap.web.de"
    imap_port = 993
    email_address = os.getenv('FROM_EMAIL_ADDRESS', 'matthias.buchhorn@web.de')
    password = os.getenv('WEBDE_APP_PASSWORD')
    alias = os.getenv('WEBDE_EMAIL_ALIAS', 'ma3u-test@email.de')
    
    print(f"📧 Debugging email fetch...")
    print(f"📬 Email address: {email_address}")
    print(f"🏷️  Alias: {alias}")
    
    try:
        # Connect to IMAP
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(email_address, password)
        mail.select('inbox')
        
        # Search for today's emails sent TO the alias (like in email_processor.py)
        today = datetime.now().strftime("%d-%b-%Y")
        print(f"📅 Searching for emails since: {today}")
        
        # Try different search approaches
        searches = [
            ('Original approach', f'(TO "{alias}") (SINCE "{today}")'),
            ('Simple TO search', f'TO "{alias}"'),
            ('Simple TO without quotes', f'TO {alias}'),
            ('All today emails', f'SINCE "{today}"'),
            ('All emails (last 10)', 'ALL')
        ]
        
        for search_name, search_criteria in searches:
            print(f"\n🔍 {search_name}: {search_criteria}")
            status, messages = mail.search(None, search_criteria)
            
            if status == 'OK':
                email_ids = messages[0].split()
                print(f"📊 Found {len(email_ids)} emails")
                
                # Check last few emails
                for email_id in email_ids[-3:]:  # Last 3 emails
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    if status == 'OK':
                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body)
                        
                        subject = email_message['Subject']
                        to_addr = email_message['To']
                        from_addr = email_message['From']
                        date = email_message['Date']
                        
                        print(f"  📧 ID: {email_id.decode()}")
                        print(f"  📅 Date: {date}")
                        print(f"  👤 From: {from_addr}")
                        print(f"  📬 To: {to_addr}")
                        print(f"  📋 Subject: {subject}")
                        
                        # Check catering keywords
                        keywords = ['catering', 'fest', 'feier', 'hochzeit', 'geburtstag']
                        text = (str(subject) + " " + str(to_addr)).lower()
                        found_keywords = [k for k in keywords if k in text]
                        if found_keywords:
                            print(f"  ✅ Catering keywords found: {found_keywords}")
                        else:
                            print(f"  ❌ No catering keywords found")
                        
                        if alias in str(to_addr):
                            print(f"  ✅ Sent to our alias!")
                        else:
                            print(f"  ❌ Not sent to our alias")
                        print()
                        
                if search_name == 'All emails (last 10)':
                    break  # Don't overwhelm with too many emails
            else:
                print(f"❌ Search failed: {status}")
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_email_fetch()