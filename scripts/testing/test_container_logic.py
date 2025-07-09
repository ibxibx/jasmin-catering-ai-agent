#!/usr/bin/env python3
"""
Test the exact same logic that Container Apps uses
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
    
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode()
                break
    else:
        body = email_message.get_payload(decode=True).decode()
    
    return body

def _is_catering_email(subject: str, body: str) -> bool:
    """Check if email is catering-related"""
    keywords = [
        'catering', 'fest', 'feier', 'hochzeit', 'geburtstag', 
        'event', 'mittagessen', 'lunch', 'dinner', 'buffet',
        'gäste', 'personen', 'büro', 'firma'
    ]
    
    text = (subject + " " + body).lower()
    return any(keyword in text for keyword in keywords)

def test_container_logic():
    """Test exact Container Apps logic"""
    
    imap_server = "imap.web.de"
    imap_port = 993
    email_address = os.getenv('FROM_EMAIL_ADDRESS', 'matthias.buchhorn@web.de')
    password = os.getenv('WEBDE_APP_PASSWORD')
    alias = os.getenv('WEBDE_EMAIL_ALIAS', 'ma3u-test@email.de')
    
    print(f"🧪 Testing Container Apps email logic...")
    print(f"📧 Email: {email_address}")
    print(f"🔑 Password: {'*' * len(password) if password else 'NOT SET'}")
    print(f"🏷️  Alias: {alias}")
    
    emails = []
    
    try:
        # Connect to IMAP - EXACT same logic as Container Apps
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(email_address, password)
        mail.select('inbox')
        
        # Search for today's emails sent TO the alias - EXACT same search
        today = datetime.now().strftime("%d-%b-%Y")
        print(f"📅 Searching with: (TO \"{alias}\") (SINCE \"{today}\")")
        status, messages = mail.search(None, f'(TO "{alias}") (SINCE "{today}")')
        
        if status == 'OK':
            email_ids = messages[0].split()
            print(f"📊 Raw search result: {email_ids}")
            # Get last 5 emails
            email_ids = email_ids[-5:] if len(email_ids) > 5 else email_ids
            print(f"📊 Processing last 5: {email_ids}")
            
            for email_id in email_ids:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status == 'OK':
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Extract subject
                    subject = _decode_subject(email_message['Subject'])
                    print(f"\n📧 Processing Email ID: {email_id.decode()}")
                    print(f"📋 Subject: {subject}")
                    
                    # Extract body
                    body = _extract_body(email_message)
                    print(f"📄 Body preview: {body[:100]}...")
                    
                    # Check if catering-related
                    is_catering = _is_catering_email(subject, body)
                    print(f"🔍 Is catering email: {is_catering}")
                    
                    if is_catering:
                        emails.append({
                            'id': email_id.decode(),
                            'subject': subject,
                            'body': body,
                            'from': email_message['From'],
                            'date': email_message['Date']
                        })
                        print(f"✅ Added to catering emails list!")
                    else:
                        print(f"❌ Not classified as catering email")
        else:
            print(f"❌ IMAP search failed: {status}")
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"❌ Exception during email fetch: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n📊 Final result: Found {len(emails)} catering emails")
    for email_data in emails:
        print(f"  📧 {email_data['id']}: {email_data['subject']}")
    
    return emails

if __name__ == "__main__":
    test_container_logic()