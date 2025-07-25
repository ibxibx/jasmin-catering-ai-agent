#!/usr/bin/env python3
"""Improved test email script with better error handling and encoding support"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import sys
from dotenv import load_dotenv

# Set encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

# Load environment variables
load_dotenv()

def send_test_email():
    """Send a test email for the Jasmin Catering AI system"""
    
    # Email configuration
    smtp_server = 'smtp.web.de'
    smtp_port = 587
    sender_email = 'ma3u-test@email.de'
    sender_password = os.getenv('WEBDE_APP_PASSWORD')
    recipient_email = 'ma3u-test@email.de'
    
    # Verify credentials are loaded
    if not sender_password:
        print("❌ Error: WEBDE_APP_PASSWORD not found in environment variables")
        print("🔧 Please check your .env file contains WEBDE_APP_PASSWORD")
        return False
    
    print(f"📧 Preparing test email...")
    print(f"   From: {sender_email}")
    print(f"   To: {recipient_email}")
    print(f"   SMTP Server: {smtp_server}:{smtp_port}")
    print(f"   Password loaded: {'✅ Yes' if sender_password else '❌ No'}")
    
    # Create test email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f'Test Catering Anfrage - {datetime.now().strftime("%H:%M:%S")}'
    
    body = f'''Sehr geehrtes Jasmin Catering Team,

Dies ist eine Test-Email für das AI Agent System.
Gesendet um: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Wir möchten ein Catering für 50 Personen anfragen für:
- Datum: {(datetime.now()).strftime("%d.%m.%Y")}
- Ort: Berlin
- Art: Finger Food und warme Gerichte
- Budget: ca. 2000 EUR

Bitte senden Sie uns drei Angebote zu.

Mit freundlichen Grüßen
Test System (AI Agent Testing)
'''
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # Send email
    try:
        print("🔄 Connecting to SMTP server...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        
        print("🔒 Starting TLS encryption...")
        server.starttls()
        
        print("🔑 Authenticating...")
        server.login(sender_email, sender_password)
        
        print("📤 Sending email...")
        server.send_message(msg)
        server.quit()
        
        print("✅ Test email sent successfully!")
        print(f"📧 Subject: {msg['Subject']}")
        print(f"⏰ Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n💡 The AI system should process this email within 5 minutes")
        print("   You can monitor the processing in Azure Container Apps logs")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("🔧 Possible solutions:")
        print("   1. Check the WEBDE_APP_PASSWORD in .env file")
        print("   2. Verify the app password is correct for ma3u-test@email.de")
        print("   3. Try generating a new app password in web.de settings")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🍽️ Jasmin Catering AI Agent - Test Email Sender")
    print("=" * 50)
    success = send_test_email()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("📊 Next steps:")
        print("   1. Wait 5 minutes for the AI system to process the email")
        print("   2. Check Azure Container Apps logs for processing details")
        print("   3. Verify the AI response in the recipient email")
    else:
        print("\n⚠️  Test failed - please check the error messages above")
        
    sys.exit(0 if success else 1)
