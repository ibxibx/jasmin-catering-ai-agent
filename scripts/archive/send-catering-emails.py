#!/usr/bin/env python3
"""
Send catering emails using the actual credentials
"""

import smtplib
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_test_catering_emails():
    """Send 5 test catering inquiry emails"""
    
    # Email configuration
    sender = os.getenv('FROM_EMAIL_ADDRESS', 'matthias.buchhorn@web.de')
    password = os.getenv('FROM_EMAIL_PASSWORD', os.getenv('WEBDE_APP_PASSWORD'))
    recipient = os.getenv('WEBDE_EMAIL_ALIAS', 'ma3u-test@email.de')
    
    if not password:
        print("❌ Error: Email password not found in environment variables")
        return False
    
    # Test emails to send
    test_emails = [
        {
            "subject": "Catering für Sommerfest - 30 Personen",
            "body": """Guten Tag,

wir benötigen Catering für unser Sommerfest am 20. Juli 2025.
- 30 Personen
- Berlin Prenzlauer Berg  
- Vegetarische Optionen wichtig

Bitte um Angebot.

MfG, Matthias Buchhorn"""
        },
        {
            "subject": "Geschäftsessen für VIP Kunden",
            "body": """Sehr geehrtes Jasmin Catering Team,

für ein wichtiges Geschäftsessen mit internationalen Kunden benötigen wir erstklassiges Catering:
- 15 Personen
- 25. Juli 2025, 19 Uhr
- Gehobenes Ambiente
- Budget: 70€ p.P.
- Besonderheit: 2 vegane Gäste

Freundliche Grüße,
Matthias Buchhorn"""
        },
        {
            "subject": "Geburtstagsfeier 50. Geburtstag",
            "body": """Hallo liebes Team,

ich plane eine große Geburtstagsfeier.
- Datum: 1. August 2025
- 60 Gäste
- Mix aus syrischen Spezialitäten
- Location: Wannsee
- Auch Kinderteller benötigt

Was können Sie uns anbieten?

Viele Grüße,
Matthias"""
        },
        {
            "subject": "Team Event - Casual Lunch",
            "body": """Hi,

unser Startup Team möchte ein entspanntes Lunch:
- 25 Personen
- 10. August 2025
- Budget: 30€ p.P.
- Viele Entwickler = viel Hunger :)
- Gerne Fingerfood und Wraps

Könnt ihr was machen?

Beste Grüße,
Matthias"""
        },
        {
            "subject": "Hochzeit Schwester - Probe Dinner",
            "body": """Sehr geehrte Damen und Herren,

meine Schwester heiratet und wir brauchen Catering für das Probe Dinner:
- 40 Personen
- 14. September 2025
- Elegantes Dinner
- Syrisch-Deutsche Fusion erwünscht
- Budget: 55€ pro Person

Bitte um detailliertes Angebot mit Weinempfehlungen.

Mit freundlichen Grüßen,
Matthias Buchhorn"""
        }
    ]
    
    try:
        print(f"📧 Connecting to web.de SMTP server...")
        server = smtplib.SMTP('smtp.web.de', 587)
        server.starttls()
        
        print(f"🔐 Logging in as {sender}...")
        server.login(sender, password)
        
        print(f"📤 Sending {len(test_emails)} test emails...")
        print()
        
        for i, email_data in enumerate(test_emails, 1):
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = recipient
            msg['Subject'] = email_data['subject']
            msg.attach(MIMEText(email_data['body'], 'plain'))
            
            server.send_message(msg)
            print(f"✅ Email {i}/5 sent: {email_data['subject']}")
        
        server.quit()
        
        print()
        print(f"🎉 All {len(test_emails)} test emails sent successfully!")
        print(f"📬 Check ma3u-test@email.de for the inquiries")
        print(f"🤖 The AI agent should process them and send responses to {sender}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print(f"❌ Authentication failed for {sender}")
        print("Please verify the email credentials in .env file")
        return False
    except Exception as e:
        print(f"❌ Error sending emails: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Jasmin Catering - Send Test Inquiry Emails")
    print("=" * 50)
    print()
    
    send_test_catering_emails()