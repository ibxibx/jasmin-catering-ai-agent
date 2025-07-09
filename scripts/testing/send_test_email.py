#!/usr/bin/env python3
"""
Quick test email sender for Jasmin Catering system
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def send_test_email():
    """Send a test catering inquiry"""
    
    # Email configuration
    smtp_server = "smtp.web.de"
    smtp_port = 587
    from_email = os.getenv('FROM_EMAIL_ADDRESS', 'matthias.buchhorn@web.de')
    password = os.getenv('WEBDE_APP_PASSWORD')
    to_email = os.getenv('WEBDE_EMAIL_ALIAS', 'ma3u-test@email.de')
    
    if not password:
        print("❌ WEBDE_APP_PASSWORD not found in environment")
        return False
    
    # Create test email
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = f"🧪 Test Catering Anfrage - Hochzeit 80 Personen - {datetime.now().strftime('%H:%M:%S')}"
    
    body = """Sehr geehrtes Jasmin Catering Team,

wir planen eine Hochzeitsfeier für 80 Personen am 15. August 2025 in Berlin.

Details:
- Datum: 15. August 2025 (Samstag)
- Uhrzeit: 17:00 - 23:00 Uhr
- Anzahl Gäste: 80 Personen
- Location: Privater Garten in Berlin-Mitte
- Anlass: Hochzeitsfeier
- Budget: Etwa 35-50€ pro Person

Wünsche:
- Vegetarische Optionen für ca. 15 Gäste
- Warmes Buffet mit syrischen Spezialitäten
- Getränke inkl. alkoholfreie Optionen
- Dekoration des Buffets

Könnten Sie uns bitte drei Angebote mit unterschiedlichen Paketen zusenden?

Vielen Dank und freundliche Grüße,
Test Familie Schmidt
Email: test@example.com
Tel: 030-12345678"""

    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        # Send email
        print(f"📧 Sending test email to {to_email}...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, [to_email], text)
        server.quit()
        
        print(f"✅ Test email sent successfully!")
        print(f"📬 Sent to: {to_email}")
        print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📋 Subject: {msg['Subject']}")
        print(f"\n⏰ The Container Apps Job runs every 5 minutes.")
        print(f"📊 Next check will be within 5 minutes...")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

if __name__ == "__main__":
    send_test_email()