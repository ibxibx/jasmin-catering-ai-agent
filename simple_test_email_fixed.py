#!/usr/bin/env python3
"""
Simple Test Email Creator - Fixed Version
Creates a test email file that demonstrates the system functionality
"""

import json
from datetime import datetime

def create_test_email():
    """Create a realistic test email for the Jasmin Catering system"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    test_email = {
        "email_id": f"test_email_{timestamp}",
        "metadata": {
            "from": "kunde@example.com", 
            "to": "ma3u-test@email.de",
            "subject": f"Catering Anfrage - Test {timestamp}",
            "date": datetime.now().isoformat(),
            "status": "ready_for_processing"
        },
        "body": f"""Sehr geehrtes Jasmin Catering Team,

wir möchten ein Catering für unsere Firmenveranstaltung beauftragen:

VERANSTALTUNGSDETAILS:
- Datum: 25.08.2025  
- Uhrzeit: 12:00 - 16:00 Uhr
- Ort: Berlin, Unter den Linden 15
- Anlass: Firmen-Sommerfest

GÄSTEANZAHL: 55 Personen

CATERING-WÜNSCHE:
- Finger Food für den Empfang (12:00-13:00)
- Warmes Buffet für das Mittagessen (13:00-15:00)  
- Kaffee & Kuchen für den Nachmittag (15:00-16:00)

BESONDERE ANFORDERUNGEN:
- 40% vegetarische Optionen
- 10% vegane Alternativen  
- 3 glutenfreie Hauptgerichte
- Berücksichtigung von Nussallergien

BUDGET: ca. 2.500 EUR

SERVICE:
- Lieferung und Aufbau bis 11:30 Uhr
- Professionelle Präsentation der Speisen
- Abholung der Materialien am Abend

Bitte senden Sie uns drei verschiedene Angebote (Basis, Standard, Premium) 
mit detaillierter Aufschlüsselung der Speisen und Preise.

Mit freundlichen Grüßen
Sarah Weber
Event Management
Mustermann & Partner GmbH

Tel: +49 30 12345678
Email: s.weber@mustermann-partner.de

---
Test Email erstellt am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Test ID: {timestamp}
Status: Bereit für AI-Processing""",
        "ai_processing_notes": {
            "extracted_info": {
                "guests": 55,
                "date": "25.08.2025",
                "location": "Berlin, Unter den Linden 15", 
                "budget": 2500,
                "special_requirements": ["vegetarian", "vegan", "gluten-free", "nut-allergy"],
                "service_type": ["finger_food", "warm_buffet", "coffee_cake"],
                "delivery_required": True
            },
            "expected_ai_response": "3 structured offers (Basis, Standard, Premium) in German with detailed menu items and pricing"
        }
    }
    
    # Save the test email
    filename = f"test_email_ready_for_ai_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(test_email, f, indent=2, ensure_ascii=False)
    
    print("Jasmin Catering - Test Email Created")
    print("=" * 50)
    print(f"SUCCESS: Test email created successfully!")
    print(f"FILE: {filename}")
    print(f"SUBJECT: {test_email['metadata']['subject']}")
    print(f"GUESTS: {test_email['ai_processing_notes']['extracted_info']['guests']}")
    print(f"BUDGET: {test_email['ai_processing_notes']['extracted_info']['budget']} EUR")
    print(f"DATE: {test_email['ai_processing_notes']['extracted_info']['date']}")
    
    print(f"\nSIMULATION: This email represents what the AI system would receive")
    print(f"            and process to generate three catering offers in German.")
    print(f"\nCONTENT: Email contains all required information:")
    print(f"         - Guest count, date, location")
    print(f"         - Budget and special dietary requirements") 
    print(f"         - Service preferences and timing")
    print(f"         - Contact information")
    
    print(f"\nNEXT STEPS:")
    print(f"    1. This email represents successful test input")
    print(f"    2. Production system (Logic App) would process similar emails")  
    print(f"    3. AI would generate 3 offers: Basis (35-40 EUR), Standard (45-50 EUR), Premium (60-70 EUR)")
    print(f"    4. Response would be sent automatically in German")
    
    return filename

if __name__ == "__main__":
    test_file = create_test_email()
    print(f"\nCOMPLETED: Test email simulation finished!")
    print(f"FILE CREATED: {test_file}")
