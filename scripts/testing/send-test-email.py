#!/usr/bin/env python3
"""Send a test email for duplicate prevention testing"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Email configuration
smtp_server = 'smtp.web.de'
smtp_port = 587
sender_email = 'ma3u-test@email.de'
sender_password = os.getenv('WEBDE_APP_PASSWORD')
recipient_email = 'ma3u-test@email.de'

# Create test email
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = recipient_email
msg['Subject'] = f'Test Catering Anfrage - {datetime.now().strftime("%H:%M:%S")}'

body = f'''Sehr geehrtes Jasmin Catering Team,

Dies ist eine Test-Email für die Duplicate Prevention Überprüfung.
Gesendet um: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Wir möchten ein Catering für 50 Personen anfragen.

Mit freundlichen Grüßen
Test System
'''

msg.attach(MIMEText(body, 'plain'))

# Send email
try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()
    print(f'✅ Test email sent successfully to {recipient_email}')
    print(f'📧 Subject: {msg["Subject"]}')
except Exception as e:
    print(f'❌ Error sending test email: {e}')