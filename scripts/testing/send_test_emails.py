#!/usr/bin/env python3
"""
Send test emails for Jasmin Catering system
"""

import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import EMAIL_CONFIG


def send_test_emails():
    """Send 5 diverse test emails"""
    
    test_scenarios = [
        {
            "subject": "Firmenfeier für 75 Mitarbeiter - Donnerstag",
            "body": """Sehr geehrtes Jasmin Catering Team,

wir planen unsere jährliche Firmenfeier:
- Datum: Nächsten Donnerstag (Werktag!)
- Anzahl: 75 Mitarbeiter
- Budget: 40€ pro Person
- Ort: Berlin Mitte
- 15 Vegetarier

Bitte um drei Angebotsoptionen.

Mit freundlichen Grüßen
Tech Innovations GmbH"""
        },
        {
            "subject": "Kulturverein Benefizgala - 120 Gäste",
            "body": """Guten Tag,

unser gemeinnütziger Kulturverein plant eine Benefizgala:
- 120 Gäste
- Syrisch-deutsche Fusion gewünscht
- Als eingetragener Verein bitten wir um Sonderkonditionen
- Vollständig Halal

Bitte um Angebot.

Berliner Kulturverein e.V."""
        },
        {
            "subject": "Dringend: Catering morgen für 25 Personen",
            "body": """Hallo,

DRINGEND für morgen:
- 25 Personen
- Budget: maximal 800€
- Lieferung nach Charlottenburg

Ist das möglich?

StartUp Berlin"""
        },
        {
            "subject": "Hochzeit im Sommer - 200 Gäste Premium",
            "body": """Für unsere Hochzeit:
- 200 Gäste
- 15. Juli (Samstag)
- Premium-Service
- Traditionelle syrische Gerichte
- Lieferort: Potsdam (30km)

Familie Al-Ahmad"""
        },
        {
            "subject": "Wöchentliches Büro-Catering - Mittwochs",
            "body": """Regelmäßiges Catering gesucht:
- Jeden Mittwoch
- 30 Personen
- Budget: 25€/Person
- Start: Nächste Woche

Digital Agency Berlin"""
        }
    ]
    
    print("📧 Sending 5 test emails...")
    print("=" * 60)
    
    sender = EMAIL_CONFIG['address']
    password = EMAIL_CONFIG['password']
    recipient = EMAIL_CONFIG['alias']
    
    try:
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(sender, password)
        
        for i, scenario in enumerate(test_scenarios, 1):
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = recipient
            msg['Subject'] = scenario['subject']
            msg['Date'] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
            
            msg.attach(MIMEText(scenario['body'], 'plain'))
            
            server.send_message(msg)
            print(f"✅ Sent {i}/5: {scenario['subject']}")
            time.sleep(1)
        
        server.quit()
        print("\n✅ All test emails sent successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    send_test_emails()