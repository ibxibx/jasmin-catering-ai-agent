#!/usr/bin/env python3
"""
Quick AI Assistant Test
Test the AI Assistant directly with a realistic catering inquiry
"""

from core.ai_assistant_openai_agent import JasminAIAssistantOpenAI
import sys
import os
from dotenv import load_dotenv

# Set encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

load_dotenv()

def test_ai_assistant():
    """Test the AI Assistant with a realistic inquiry"""
    
    print("Testing Jasmin Catering AI Assistant")
    print("=" * 50)
    
    try:
        # Initialize AI Assistant
        print("Initializing AI Assistant...")
        ai = JasminAIAssistantOpenAI()
        print(f"SUCCESS: Connected to Assistant {ai.assistant_id}")
        
        # Test query in German
        test_subject = "Catering Anfrage für Firmenveranstaltung"
        test_query = """Sehr geehrtes Jasmin Catering Team,

wir möchten ein Catering für unsere Firmenveranstaltung beauftragen:

- Datum: 15.09.2025
- Uhrzeit: 12:00 - 18:00 Uhr  
- Ort: Berlin, Alexanderplatz
- Anlass: Firmenjubiläum
- Gästeanzahl: 35 Personen
- Budget: ca. 1800 EUR

Gewünschte Leistungen:
- Finger Food für den Empfang
- Warmes Buffet zum Mittagessen
- Vegetarische und vegane Optionen

Bitte senden Sie uns drei verschiedene Angebote.

Mit freundlichen Grüßen
Thomas Mueller
Event Manager"""

        print("Generating AI response...")
        print("Query:", test_subject)
        print("Length:", len(test_query), "characters")
        
        # Generate response
        response = ai.generate_response(test_subject, test_query)
        
        if response:
            print("SUCCESS: AI response generated!")
            print("Response length:", len(response), "characters")
            print("=" * 50)
            print("AI RESPONSE:")
            print("=" * 50)
            print(response)
            print("=" * 50)
            
            # Save response to file
            filename = f"ai_test_response_{ai.assistant_id[-8:]}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"AI Assistant Test Response\n")
                f.write(f"Assistant ID: {ai.assistant_id}\n")
                f.write(f"Timestamp: {ai.timestamp if hasattr(ai, 'timestamp') else 'N/A'}\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"QUERY:\n{test_query}\n\n")
                f.write(f"RESPONSE:\n{response}\n")
            
            print(f"Response saved to: {filename}")
            return True
            
        else:
            print("ERROR: No response generated")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_ai_assistant()
    if success:
        print("\nSUCCESS: AI Assistant is working perfectly!")
        print("The system can generate professional German catering offers.")
    else:
        print("\nFAILED: AI Assistant test unsuccessful")
