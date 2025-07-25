#!/usr/bin/env python3
"""
Quick AI Assistant Test - ASCII Version
Tests the AI assistant with a realistic catering query
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_ai_assistant():
    """Test the AI assistant directly"""
    print("TESTING: Jasmin Catering AI Assistant")
    print("=" * 50)
    
    try:
        # Import the AI assistant
        from core.ai_assistant_openai_agent import JasminAIAssistantOpenAI
        
        # Initialize
        print("INITIALIZING: AI Assistant...")
        ai = JasminAIAssistantOpenAI()
        print(f"SUCCESS: AI Assistant initialized")
        print(f"   Assistant ID: {ai.assistant_id}")
        
        # Test query in German
        test_subject = "Catering Anfrage für Firmenveranstaltung"
        test_query = """Sehr geehrtes Jasmin Catering Team,

wir möchten ein Catering für unsere Firmenveranstaltung beauftragen:

- Datum: 30.08.2025
- Ort: Berlin, Alexanderplatz
- Gäste: 40 Personen
- Art: Finger Food + warmes Buffet
- Budget: ca. 1800 EUR
- Besonders: 30% vegetarische Optionen

Bitte senden Sie uns drei Angebote (Basis, Standard, Premium).

Mit freundlichen Grüßen
Thomas Mueller
Event Manager"""

        print("PROCESSING: Sending query to AI Assistant...")
        print(f"   Subject: {test_subject}")
        print(f"   Query length: {len(test_query)} characters")
        
        # Generate response
        response = ai.generate_response(test_subject, test_query)
        
        if response:
            print(f"SUCCESS: AI Response generated!")
            print(f"   Response length: {len(response)} characters")
            
            # Save full response to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_response_test_{timestamp}.txt"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"JASMIN CATERING AI RESPONSE TEST\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Assistant ID: {ai.assistant_id}\n\n")
                f.write(f"ORIGINAL QUERY:\n{'-' * 20}\n{test_query}\n\n")
                f.write(f"AI RESPONSE:\n{'-' * 20}\n{response}\n")
            
            print(f"SAVED: Full response saved to: {filename}")
            
            # Show preview
            print(f"\nPREVIEW: Response (first 500 characters):")
            print("-" * 50)
            print(response[:500] + "..." if len(response) > 500 else response)
            print("-" * 50)
            
            # Analyze response
            checks = []
            if "Angebot" in response and "EUR" in response:
                checks.append("Contains offers and pricing")
            if "vegetarisch" in response.lower():
                checks.append("Addresses vegetarian requirements")
            if "Basis" in response and "Standard" in response and "Premium" in response:
                checks.append("Contains three package levels")
            
            print(f"ANALYSIS: Response quality checks:")
            for check in checks:
                print(f"   + {check}")
            
            return True
            
        else:
            print("ERROR: No response generated")
            return False
            
    except Exception as e:
        print(f"ERROR: Testing AI Assistant failed: {e}")
        return False

if __name__ == "__main__":
    success = test_ai_assistant()
    if success:
        print("\nCOMPLETED: AI Assistant test successful!")
    else:
        print("\nFAILED: AI Assistant test unsuccessful")
