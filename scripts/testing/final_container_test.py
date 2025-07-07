#!/usr/bin/env python3
"""
Final test that exactly mimics Container Apps execution
"""

import imaplib
import email
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def _decode_subject(subject: str) -> str:
    """Decode email subject if encoded"""
    if not subject:
        return "No Subject"
        
    try:
        decoded = email.header.decode_header(subject)[0]
        if decoded[1]:
            return decoded[0].decode(decoded[1])
        return str(decoded[0])
    except:
        return str(subject)

def _extract_body(email_message) -> str:
    """Extract plain text body from email"""
    body = ""
    
    try:
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
        else:
            payload = email_message.get_payload(decode=True)
            if payload:
                body = payload.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error extracting body: {e}")
        body = ""
    
    return body

def _is_catering_email(subject: str, body: str) -> bool:
    """Check if email is catering-related"""
    keywords = [
        'catering', 'fest', 'feier', 'hochzeit', 'geburtstag', 
        'event', 'mittagessen', 'lunch', 'dinner', 'buffet',
        'gäste', 'personen', 'büro', 'firma'
    ]
    
    text = (subject + " " + body).lower()
    found_keywords = [k for k in keywords if k in text]
    
    if found_keywords:
        print(f"    🔍 Found catering keywords: {found_keywords}")
        return True
    else:
        print(f"    ❌ No catering keywords found in: {text[:100]}...")
        return False

def fetch_catering_emails_exact():
    """EXACT replica of Container Apps fetch_catering_emails method"""
    
    # Use the exact same configuration as Container Apps
    imap_server = "imap.web.de"
    imap_port = 993
    smtp_server = "smtp.web.de" 
    smtp_port = 587
    email_address = os.getenv('FROM_EMAIL_ADDRESS', 'matthias.buchhorn@web.de')
    password = os.getenv('WEBDE_APP_PASSWORD')
    alias = os.getenv('WEBDE_EMAIL_ALIAS', 'ma3u-test@email.de')
    
    print(f"🧪 EXACT Container Apps Email Processing Test")
    print(f"=" * 50)
    print(f"📧 IMAP Server: {imap_server}:{imap_port}")
    print(f"📧 SMTP Server: {smtp_server}:{smtp_port}")
    print(f"👤 Email Address: {email_address}")
    print(f"🏷️  Alias: {alias}")
    print(f"🔑 Password: {'*' * len(password) if password else 'NOT SET'}")
    
    emails = []
    limit = 5
    
    try:
        print(f"\n🔌 Connecting to IMAP...")
        # Connect to IMAP - EXACT same as EmailProcessor
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        print(f"✅ IMAP connection established")
        
        print(f"🔐 Logging in...")
        mail.login(email_address, password)
        print(f"✅ Login successful")
        
        print(f"📁 Selecting inbox...")
        mail.select('inbox')
        print(f"✅ Inbox selected")
        
        # Search for today's emails sent TO the alias - EXACT same search
        today = datetime.now().strftime("%d-%b-%Y")
        search_query = f'(TO "{alias}") (SINCE "{today}")'
        print(f"\n🔍 Searching with query: {search_query}")
        print(f"📅 Today's date format: {today}")
        
        status, messages = mail.search(None, search_query)
        print(f"📊 Search status: {status}")
        
        if status == 'OK':
            email_ids = messages[0].split()
            print(f"📊 Raw email IDs found: {email_ids}")
            
            # Get last N emails - EXACT same logic
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            print(f"📊 Processing last {limit}: {email_ids}")
            
            for i, email_id in enumerate(email_ids):
                print(f"\n📧 Processing email {i+1}/{len(email_ids)}: {email_id.decode()}")
                
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status == 'OK':
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Extract subject - EXACT same method
                    subject = _decode_subject(email_message['Subject'])
                    print(f"  📋 Subject: {subject}")
                    
                    # Extract body - EXACT same method  
                    body = _extract_body(email_message)
                    print(f"  📄 Body length: {len(body)} chars")
                    print(f"  📄 Body preview: {body[:100]}...")
                    
                    # Check if catering-related - EXACT same method
                    print(f"  🔍 Checking if catering-related...")
                    if _is_catering_email(subject, body):
                        print(f"  ✅ CATERING EMAIL DETECTED!")
                        emails.append({
                            'id': email_id.decode(),
                            'subject': subject,
                            'body': body,
                            'from': email_message['From'],
                            'date': email_message['Date']
                        })
                    else:
                        print(f"  ❌ Not detected as catering email")
                else:
                    print(f"  ❌ Failed to fetch email: {status}")
        else:
            print(f"❌ Search failed: {status}")
        
        print(f"\n📁 Closing connection...")
        mail.close()
        mail.logout()
        print(f"✅ Connection closed")
        
    except Exception as e:
        print(f"❌ Exception during email fetch: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n📊 FINAL RESULT:")
    print(f"🎯 Found {len(emails)} catering emails")
    
    if emails:
        print(f"✅ SUCCESS - Catering emails found:")
        for email_data in emails:
            print(f"  📧 {email_data['id']}: {email_data['subject']}")
    else:
        print(f"❌ NO CATERING EMAILS FOUND (same as Container Apps)")
        print(f"🔍 This means Container Apps should be finding emails...")
        print(f"💡 The issue might be:")
        print(f"   - Environment variable differences")
        print(f"   - Timezone differences")
        print(f"   - Network connectivity in Container Apps")
        print(f"   - Error handling hiding the real issue")
    
    return emails

if __name__ == "__main__":
    fetch_catering_emails_exact()