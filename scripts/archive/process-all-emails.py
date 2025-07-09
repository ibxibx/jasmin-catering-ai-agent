#!/usr/bin/env python3
"""
Process all catering emails with broader search criteria
"""

import imaplib
import email
import smtplib
import os
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def get_all_catering_emails():
    """Get all catering-related emails from today"""
    
    email_address = "matthias.buchhorn@web.de"
    password = os.getenv('WEBDE_APP_PASSWORD')
    
    try:
        print("📬 Connecting to email server...")
        mail = imaplib.IMAP4_SSL('imap.web.de', 993)
        mail.login(email_address, password)
        mail.select('inbox')
        
        # Broader search - all emails from today
        today = datetime.now().strftime("%d-%b-%Y")
        status, messages = mail.search(None, f'(FROM "matthias.buchhorn@web.de") (SINCE "{today}")')
        
        emails = []
        if status == 'OK':
            email_ids = messages[0].split()
            print(f"📧 Found {len(email_ids)} total emails from today")
            
            for email_id in email_ids:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status == 'OK':
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    subject = email_message['Subject']
                    
                    # Decode subject if encoded
                    if subject:
                        decoded_subject = email.header.decode_header(subject)[0]
                        if decoded_subject[1]:
                            subject = decoded_subject[0].decode(decoded_subject[1])
                        else:
                            subject = str(decoded_subject[0])
                    
                    # Only process catering-related emails
                    catering_keywords = ['catering', 'sommerfest', 'geschäft', 'geburtstag', 'team', 'hochzeit', 'lunch', 'dinner']
                    if any(keyword.lower() in subject.lower() for keyword in catering_keywords):
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
                            'body': body,
                            'id': email_id.decode(),
                            'date': email_message['Date']
                        })
        
        mail.close()
        mail.logout()
        
        # Remove duplicates by subject
        unique_emails = []
        seen_subjects = set()
        for email_data in emails:
            if email_data['subject'] not in seen_subjects:
                unique_emails.append(email_data)
                seen_subjects.add(email_data['subject'])
        
        return unique_emails
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def generate_ai_response(email_data):
    """Generate AI response"""
    api_key = os.getenv('AZURE_AI_API_KEY')
    
    try:
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

Erstelle immer drei Angebotsoptionen und gehe auf spezifische Wünsche ein. Der Kunde heißt Herr Buchhorn."""
                },
                {
                    "role": "user",
                    "content": f"""Erstelle ein professionelles Angebot für:

Betreff: {email_data['subject']}

Anfrage:
{email_data['body']}

Beginne mit 'Sehr geehrter Herr Buchhorn,' und erstelle drei Angebotsoptionen."""
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
            return response.json()['choices'][0]['message']['content']
        return None
        
    except Exception as e:
        print(f"❌ AI Error: {e}")
        return None

def send_response(original_email, ai_response):
    """Send AI response"""
    sender = "ma3u-test@email.de"
    recipient = "matthias.buchhorn@web.de"
    password = os.getenv('WEBDE_APP_PASSWORD')
    
    try:
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = f"Re: {original_email['subject']} - Angebot Jasmin Catering"
        
        full_response = f"""{ai_response}

--
Jasmin Catering Berlin
Syrische Fusion-Küche
Tel: 030-12345678
E-Mail: ma3u-test@email.de

🤖 Automatisch generiert vom Jasmin Catering AI Agent
"""
        
        msg.attach(MIMEText(full_response, 'plain'))
        
        server = smtplib.SMTP('smtp.web.de', 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"❌ Send Error: {e}")
        return False

def main():
    print("🤖 Jasmin Catering AI - Process All Emails")
    print("=" * 45)
    
    emails = get_all_catering_emails()
    
    if not emails:
        print("📭 No catering emails found")
        return
    
    print(f"📧 Found {len(emails)} unique catering emails:")
    for i, email_data in enumerate(emails, 1):
        print(f"   {i}. {email_data['subject']}")
    print()
    
    for i, email_data in enumerate(emails, 1):
        print(f"🔄 Processing {i}/{len(emails)}: {email_data['subject']}")
        
        ai_response = generate_ai_response(email_data)
        if ai_response:
            if send_response(email_data, ai_response):
                print(f"   ✅ Response sent!")
            else:
                print(f"   ❌ Failed to send")
        else:
            print(f"   ❌ Failed to generate response")
        print()
    
    print("🎉 All emails processed!")
    print("📬 Check matthias.buchhorn@web.de for AI responses")

if __name__ == "__main__":
    main()