#!/usr/bin/env python3
"""
Send generated email responses via web.de SMTP
Since ma3u-test@email.de is an alias for matthias.buchhorn@web.de,
we can send emails to matthias.buchhorn@web.de directly.
"""

import smtplib
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_test_email():
    """Send a test email to verify SMTP configuration"""
    
    # Email configuration
    sender = "ma3u-test@email.de"
    recipient = "matthias.buchhorn@web.de"
    
    # Note: You need to set the WEBDE_APP_PASSWORD environment variable
    # or add it to your .env file
    password = os.getenv('WEBDE_APP_PASSWORD')
    
    if not password:
        print("❌ Error: WEBDE_APP_PASSWORD not set in environment variables")
        print("Please set it using: export WEBDE_APP_PASSWORD='your-app-password'")
        return False
    
    # Create a sample catering response
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = f'Jasmin Catering - Angebot für Ihre Anfrage ({datetime.now().strftime("%d.%m.%Y")})'
    
    body = """Sehr geehrte/r Kunde/in,

vielen Dank für Ihre Catering-Anfrage bei Jasmin Catering!

Dies ist eine Test-Email, um die Email-Integration zu überprüfen.

In der finalen Version erhalten Sie hier ein detailliertes Angebot mit:
- Drei Preisoptionen (Basis, Standard, Premium)
- Speziell auf Ihre Wünsche abgestimmte Menüvorschläge
- Unsere syrischen Fusion-Spezialitäten
- Vegetarische und vegane Optionen

Mit freundlichen Grüßen,
Ihr Jasmin Catering Team

---
Diese Email wurde automatisch vom Jasmin Catering AI Agent generiert.
"""
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # Connect to web.de SMTP server
        print(f"📧 Connecting to web.de SMTP server...")
        server = smtplib.SMTP('smtp.web.de', 587)
        server.starttls()
        
        print(f"🔐 Logging in as {sender}...")
        server.login(sender, password)
        
        print(f"📤 Sending email to {recipient}...")
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Test email sent successfully!")
        print(f"📬 Check your inbox at: {recipient}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print(f"❌ Authentication failed. Please check your app password.")
        print("To get an app password: https://web.de > Settings > Security > App Passwords")
        return False
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Jasmin Catering Email Test")
    print("=" * 40)
    
    # Check if password is provided as argument
    if len(sys.argv) > 1:
        os.environ['WEBDE_APP_PASSWORD'] = sys.argv[1]
    
    send_test_email()