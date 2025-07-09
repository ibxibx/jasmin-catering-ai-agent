#!/usr/bin/env python3
"""
Monitor for real emails and send AI responses
This simulates what the Logic App should do with real email integration
"""

import imaplib
import email
import smtplib
import os
import json
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def check_for_new_emails():
    """Check ma3u-test@email.de for new catering inquiries"""
    
    # Since ma3u-test@email.de is an alias, we check matthias.buchhorn@web.de
    email_address = "matthias.buchhorn@web.de"
    password = os.getenv('WEBDE_APP_PASSWORD')
    
    if not password:
        print("❌ No email password found")
        return []
    
    try:
        print("📬 Checking for new emails...")
        
        # Connect to IMAP server
        mail = imaplib.IMAP4_SSL('imap.web.de', 993)
        mail.login(email_address, password)
        
        # Select inbox
        mail.select('inbox')
        
        # Search for catering related emails from today
        today = datetime.now().strftime("%d-%b-%Y")
        status, messages = mail.search(None, f'(FROM "matthias.buchhorn@web.de") (SINCE "{today}") (SUBJECT "Catering")')
        
        emails = []
        if status == 'OK':
            email_ids = messages[0].split()
            print(f"📧 Found {len(email_ids)} potential catering emails")
            
            for email_id in email_ids[-5:]:  # Get last 5 emails
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status == 'OK':
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    subject = email_message['Subject']
                    from_addr = email_message['From']
                    
                    # Get email body
                    body = ""
                    if email_message.is_multipart():
                        for part in email_message.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = email_message.get_payload(decode=True).decode()
                    
                    emails.append({
                        'subject': subject,
                        'from': from_addr,
                        'body': body,
                        'id': email_id.decode()
                    })
        
        mail.close()
        mail.logout()
        return emails
        
    except Exception as e:
        print(f"❌ Error checking emails: {e}")
        return []

def generate_ai_response(email_data):
    """Generate AI response for catering inquiry"""
    
    api_key = os.getenv('AZURE_AI_API_KEY')
    if not api_key:
        print("❌ No AI API key found")
        return None
    
    try:
        print(f"🤖 Generating AI response for: {email_data['subject']}")
        
        headers = {
            'Content-Type': 'application/json',
            'api-key': api_key
        }
        
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": """Du bist der Kundenberater von Jasmin Catering, einem syrischen Fusion-Catering in Berlin. Erstelle professionelle, personalisierte Angebote auf Deutsch für Catering-Anfragen.

Wichtige Informationen:
- Preise: 25-35€ (Basis), 35-45€ (Standard), 50-70€ (Premium) pro Person
- Liefergebiet: Berlin und Umgebung (bis 50km)
- Spezialität: Syrische Fusion-Küche
- Optionen: Halal, vegetarisch, vegan verfügbar
- Mindestbestellung: 10 Personen

Erstelle immer drei Angebotsoptionen und gehe auf spezifische Wünsche ein. Schließe mit einer Einladung zum persönlichen Gespräch.

Der Kunde heißt immer Herr Buchhorn (Matthias Buchhorn)."""
                },
                {
                    "role": "user",
                    "content": f"""Erstelle ein professionelles Angebot für folgende Anfrage:

Betreff: {email_data['subject']}

Anfrage:
{email_data['body']}

Erstelle ein persönliches Angebot mit drei Optionen. Beginne mit 'Sehr geehrter Herr Buchhorn,' und verwende einen freundlichen, professionellen Ton."""
                }
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        response = requests.post(
            'https://swedencentral.api.cognitive.microsoft.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-01',
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            print(f"❌ AI API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error generating AI response: {e}")
        return None

def send_response_email(original_email, ai_response):
    """Send AI-generated response back to customer"""
    
    sender = "ma3u-test@email.de"
    recipient = "matthias.buchhorn@web.de"
    password = os.getenv('WEBDE_APP_PASSWORD')
    
    try:
        print(f"📤 Sending response for: {original_email['subject']}")
        
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = f"Re: {original_email['subject']} - Ihr Angebot von Jasmin Catering"
        
        full_response = f"""{ai_response}

--
Jasmin Catering
Syrische Fusion-Küche für Ihre besonderen Anlässe
Tel: 030-12345678
E-Mail: ma3u-test@email.de
Web: www.jasmincatering.de

Diese Email wurde automatisch vom Jasmin Catering AI Agent generiert.
"""
        
        msg.attach(MIMEText(full_response, 'plain'))
        
        server = smtplib.SMTP('smtp.web.de', 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Response sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error sending response: {e}")
        return False

def main():
    print("🤖 Jasmin Catering AI Email Monitor")
    print("=" * 40)
    print("Checking for catering inquiries and sending AI responses...")
    print()
    
    # Check for new emails
    emails = check_for_new_emails()
    
    if not emails:
        print("📭 No new catering emails found")
        return
    
    print(f"📧 Processing {len(emails)} emails...")
    print()
    
    for i, email_data in enumerate(emails, 1):
        print(f"🔄 Processing email {i}/{len(emails)}")
        print(f"   Subject: {email_data['subject']}")
        
        # Generate AI response
        ai_response = generate_ai_response(email_data)
        
        if ai_response:
            # Send response
            if send_response_email(email_data, ai_response):
                print(f"   ✅ Complete!")
            else:
                print(f"   ❌ Failed to send response")
        else:
            print(f"   ❌ Failed to generate AI response")
        
        print()
    
    print("🎉 Email processing complete!")
    print("📬 Check matthias.buchhorn@web.de for AI responses")

if __name__ == "__main__":
    main()