#!/usr/bin/env python3
"""
Check for the new test email: Hochzeitsfeier für 80 Personen - 16. August 2025
"""

import imaplib
import email
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def check_new_email():
    """Check for the latest test email"""
    
    imap_server = "imap.web.de"
    imap_port = 993
    email_address = os.getenv('FROM_EMAIL_ADDRESS', 'matthias.buchhorn@web.de')
    password = os.getenv('WEBDE_APP_PASSWORD')
    alias = os.getenv('WEBDE_EMAIL_ALIAS', 'ma3u-test@email.de')
    
    print(f"📧 Checking for new email: 'Hochzeitsfeier für 80 Personen - 16. August 2025'")
    print(f"🕐 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Connect to IMAP
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(email_address, password)
        mail.select('inbox')
        
        # Search for recent emails to our alias
        status, messages = mail.search(None, f'TO "{alias}"')
        
        if status == 'OK':
            email_ids = messages[0].split()
            print(f"📊 Total emails to alias: {len(email_ids)}")
            
            # Check the most recent emails
            recent_emails = email_ids[-5:] if len(email_ids) > 5 else email_ids
            print(f"📊 Checking last 5 emails: {recent_emails}")
            
            found_new_email = False
            
            for email_id in recent_emails:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status == 'OK':
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    subject = email_message['Subject']
                    date = email_message['Date']
                    from_addr = email_message['From']
                    
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
                    print(f"📋 Subject: {subject}")
                    
                    # Check if this is our new test email
                    if "Hochzeitsfeier" in str(subject) and "16. August 2025" in str(subject):
                        found_new_email = True
                        print(f"🎯 FOUND THE NEW TEST EMAIL!")
                        print(f"  📧 Email ID: {email_id.decode()}")
                        print(f"  📋 Subject: {subject}")
                        print(f"  📅 Date: {date}")
                        
                        # Check catering keywords
                        keywords = ['hochzeit', 'feier', 'personen', 'august']
                        found_keywords = [k for k in keywords if k.lower() in subject.lower()]
                        print(f"  🔍 Catering keywords found: {found_keywords}")
                        
                        if found_keywords:
                            print(f"  ✅ This email SHOULD be detected by Container Apps!")
                        else:
                            print(f"  ❌ This email might not be detected as catering")
                    
                    elif "Hochzeitsfeier" in str(subject) or "hochzeit" in str(subject).lower():
                        print(f"  🔍 Related wedding email but not the exact new one")
            
            if not found_new_email:
                print(f"\n❌ New test email not found yet")
                print(f"💡 It might still be in transit or not arrived yet")
            else:
                print(f"\n✅ New test email confirmed in inbox!")
                
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"❌ Error checking emails: {e}")

if __name__ == "__main__":
    check_new_email()