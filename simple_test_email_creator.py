#!/usr/bin/env python3
"""
Simple Test Email Simulator
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
            "subject": f"🍽️ Catering Anfrage - Test {timestamp}",
            "date": datetime.now().isoformat(),
            "status": "ready_for_processing"
        },
        "body": f"""Sehr geehrtes Jasmin Catering Team,

wir möchten ein Catering für unsere Firmenveranstaltung beauftragen:

📅 **Veranstaltungsdetails:**
- Datum: 25.08.2025  
- Uhrzeit: 12:00 - 16:00 Uhr
- Ort: Berlin, Unter den Linden 15
- Anlass: Firmen-Sommerfest

👥 **Gästeanzahl:** 55 Personen

🍽️ **Catering-Wünsche:**
- Finger Food für den Empfang (12:00-13:00)
- Warmes Buffet für das Mittagessen (13:00-15:00)  
- Kaffee & Kuchen für den Nachmittag (15:00-16:00)

🌱 **Besondere Anforderungen:**
- 40% vegetarische Optionen
- 10% vegane Alternativen  
- 3 glutenfreie Hauptgerichte
- Berücksichtigung von Nussallergien

💰 **Budget:** ca. 2.500 EUR

📦 **Service:**
- Lieferung und Aufbau bis 11:30 Uhr
- Professionelle Präsentation der Speisen
- Abholung der Materialien am Abend

Bitte senden Sie uns drei verschiedene Angebote (Basis, Standard, Premium) 
mit detaillierter Aufschlüsselung der Speisen und Preise.

Mit freundlichen Grüßen
Sarah Weber
Event Management
Mustermann & Partner GmbH

📞 Tel: +49 30 12345678
📧 Email: s.weber@mustermann-partner.de

---
🤖 Test Email erstellt am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📋 Test ID: {timestamp}
🔧 Status: Bereit für AI-Processing""",
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
        },
        "test_metadata": {
            "created_by": "Working Test Email Solution",
            "purpose": "Demonstrate realistic catering inquiry processing",
            "ai_assistant_ready": True,
            "processing_status": "pending"
        }
    }
    
    # Save the test email
    filename = f"test_email_ready_for_ai_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(test_email, f, indent=2, ensure_ascii=False)
    
    print("🍽️ Jasmin Catering - Test Email Created")
    print("=" * 50)
    print(f"✅ Test email created successfully!")
    print(f"💾 Saved as: {filename}")
    print(f"📧 Subject: {test_email['metadata']['subject']}")
    print(f"👥 Guests: {test_email['ai_processing_notes']['extracted_info']['guests']}")
    print(f"💰 Budget: €{test_email['ai_processing_notes']['extracted_info']['budget']}")
    print(f"📅 Date: {test_email['ai_processing_notes']['extracted_info']['date']}")
    
    print(f"\n🤖 This email simulates what the AI system would receive")
    print(f"   and process to generate three catering offers in German.")
    print(f"\n📊 Email contains all required information:")
    print(f"   ✅ Guest count, date, location")
    print(f"   ✅ Budget and special dietary requirements") 
    print(f"   ✅ Service preferences and timing")
    print(f"   ✅ Contact information")
    
    print(f"\n🎯 Next steps:")
    print(f"   1. This email represents successful test input")
    print(f"   2. Production system (Logic App) would process similar emails")  
    print(f"   3. AI would generate 3 offers: Basis (€35-40), Standard (€45-50), Premium (€60-70)")
    print(f"   4. Response would be sent automatically in German")
    
    return filename

if __name__ == "__main__":
    test_file = create_test_email()
    print(f"\n🎉 Test email simulation completed!")
    print(f"📁 File created: {test_file}")
