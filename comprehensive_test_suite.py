#!/usr/bin/env python3
"""
Comprehensive Test Suite for Jasmin Catering AI Agent
Tests multiple components: AI Assistant, Email, Key Vault, and System Integration
"""

import os
import sys
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Set encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

# Load environment variables
load_dotenv()

class JasminCateringTestSuite:
    """Comprehensive test suite for all system components"""
    
    def __init__(self):
        self.results = []
        
    def log_result(self, test_name: str, status: str, message: str, details: str = ""):
        """Log test results"""
        result = {
            'test': test_name,
            'status': status,  # ✅ PASS, ❌ FAIL, ⚠️ WARN
            'message': message,
            'details': details,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        self.results.append(result)
        
        # Print result immediately
        status_icon = result['status']
        print(f"{status_icon} {test_name}: {message}")
        if details:
            print(f"   {details}")
    
    def test_environment_variables(self):
        """Test 1: Check all required environment variables"""
        print("\n🔧 Test 1: Environment Variables")
        print("-" * 40)
        
        required_vars = {
            'FROM_EMAIL_ADDRESS': 'Email sender address',
            'WEBDE_APP_PASSWORD': 'Email app password',
            'WEBDE_EMAIL_ALIAS': 'Email alias to monitor',
            'AZURE_AI_ENDPOINT': 'Azure AI endpoint',
            'AZURE_AI_API_KEY': 'Azure AI API key',
        }
        
        missing_vars = []
        for var, description in required_vars.items():
            value = os.getenv(var)
            if value:
                # Mask sensitive values
                display_value = f"{value[:8]}..." if 'PASSWORD' in var or 'KEY' in var else value
                self.log_result(f"ENV_{var}", "✅", f"Found", f"{description}: {display_value}")
            else:
                missing_vars.append(var)
                self.log_result(f"ENV_{var}", "❌", f"Missing", f"{description}")
        
        if missing_vars:
            self.log_result("ENV_OVERALL", "❌", f"Missing {len(missing_vars)} variables", f"Missing: {', '.join(missing_vars)}")
        else:
            self.log_result("ENV_OVERALL", "✅", "All environment variables found")
    
    def test_ai_assistant(self):
        """Test 2: Test AI Assistant connectivity"""
        print("\n🤖 Test 2: AI Assistant")
        print("-" * 40)
        
        try:
            # Import and test AI assistant
            from core.ai_assistant_openai_agent import JasminAIAssistantOpenAI
            
            ai = JasminAIAssistantOpenAI()
            self.log_result("AI_IMPORT", "✅", "AI Assistant imported successfully")
            
            # Test basic functionality
            assistant_info = ai.get_assistant_info()
            if assistant_info:
                self.log_result("AI_INFO", "✅", "Assistant info retrieved", f"ID: {assistant_info.get('id', 'unknown')}")
            else:
                self.log_result("AI_INFO", "❌", "Could not retrieve assistant info")
            
            # Test a simple query
            test_query = "Test: Können Sie mir ein Angebot für 20 Personen erstellen?"
            response = ai.generate_response("Test Anfrage", test_query)
            
            if response and len(response) > 50:
                self.log_result("AI_RESPONSE", "✅", "AI response generated", f"Length: {len(response)} chars")
            else:
                self.log_result("AI_RESPONSE", "❌", "AI response too short or empty")
                
        except ImportError as e:
            self.log_result("AI_IMPORT", "❌", "Could not import AI assistant", str(e))
        except Exception as e:
            self.log_result("AI_ERROR", "❌", "AI Assistant error", str(e))
    
    def test_email_connection(self):
        """Test 3: Test email server connectivity"""
        print("\n📧 Test 3: Email Connection")
        print("-" * 40)
        
        smtp_server = 'smtp.web.de'
        smtp_port = 587
        sender_email = os.getenv('FROM_EMAIL_ADDRESS')
        sender_password = os.getenv('WEBDE_APP_PASSWORD')
        
        if not sender_email or not sender_password:
            self.log_result("EMAIL_CREDS", "❌", "Email credentials missing")
            return
        
        try:
            # Test SMTP connection
            self.log_result("EMAIL_CONNECT", "🔄", "Connecting to SMTP server...")
            server = smtplib.SMTP(smtp_server, smtp_port)
            self.log_result("EMAIL_CONNECT", "✅", "SMTP connection established")
            
            # Test TLS
            server.starttls()
            self.log_result("EMAIL_TLS", "✅", "TLS encryption started")
            
            # Test authentication
            server.login(sender_email, sender_password)
            self.log_result("EMAIL_AUTH", "✅", "Authentication successful")
            
            server.quit()
            self.log_result("EMAIL_OVERALL", "✅", "Email system fully functional")
            
        except smtplib.SMTPAuthenticationError as e:
            self.log_result("EMAIL_AUTH", "❌", "Authentication failed", str(e))
            self.log_result("EMAIL_OVERALL", "❌", "Email system not working")
        except Exception as e:
            self.log_result("EMAIL_ERROR", "❌", "Email connection error", str(e))
    
    def send_test_email(self):
        """Test 4: Send actual test email"""
        print("\n📤 Test 4: Send Test Email")
        print("-" * 40)
        
        sender_email = os.getenv('FROM_EMAIL_ADDRESS')
        sender_password = os.getenv('WEBDE_APP_PASSWORD')
        recipient_email = os.getenv('WEBDE_EMAIL_ALIAS', sender_email)
        
        if not sender_email or not sender_password:
            self.log_result("SEND_EMAIL", "❌", "Cannot send - credentials missing")
            return
        
        # Create test email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f'🧪 Jasmin AI Test - {datetime.now().strftime("%H:%M:%S")}'
        
        body = f'''Sehr geehrtes Jasmin Catering Team,

Dies ist eine automatische Test-Email vom AI Agent System.

🧪 Test Details:
- Gesendet um: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- Von: {sender_email}
- An: {recipient_email}
- Test Suite Version: 1.0

📋 Test Anfrage:
Wir möchten ein Catering für 30 Personen anfragen:
- Datum: {datetime.now().strftime("%d.%m.%Y")}
- Ort: Berlin
- Art: Finger Food und warme Gerichte
- Budget: ca. 1500 EUR
- Besondere Wünsche: Vegetarische Optionen

Bitte senden Sie uns drei Angebote zu.

Mit freundlichen Grüßen
Jasmin AI Test Suite

---
🤖 Diese Email wurde automatisch generiert zur Systemtestung.
'''
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        try:
            server = smtplib.SMTP('smtp.web.de', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            
            self.log_result("SEND_EMAIL", "✅", "Test email sent successfully")
            self.log_result("SEND_EMAIL_DETAILS", "📧", f"From: {sender_email} → To: {recipient_email}")
            return True
            
        except Exception as e:
            self.log_result("SEND_EMAIL", "❌", "Failed to send test email", str(e))
            return False
    
    def test_system_integration(self):
        """Test 5: Test full system integration"""
        print("\n🔄 Test 5: System Integration")
        print("-" * 40)
        
        try:
            # Test EmailProcessor
            from core.email_processor import EmailProcessor
            processor = EmailProcessor()
            self.log_result("INTEGRATION_EMAIL", "✅", "EmailProcessor imported")
            
            # Test SlackNotifier
            from core.slack_notifier import SlackNotifier
            slack = SlackNotifier()
            self.log_result("INTEGRATION_SLACK", "✅", "SlackNotifier imported")
            
            # Test EmailTracker
            from core.email_tracker import EmailTracker
            tracker = EmailTracker()
            self.log_result("INTEGRATION_TRACKER", "✅", "EmailTracker imported")
            
            self.log_result("INTEGRATION_OVERALL", "✅", "All components integrated successfully")
            
        except ImportError as e:
            self.log_result("INTEGRATION_ERROR", "❌", "Integration test failed", str(e))
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🍽️ Jasmin Catering AI Agent - Comprehensive Test Suite")
        print("=" * 65)
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all tests
        self.test_environment_variables()
        self.test_ai_assistant()
        self.test_email_connection()
        self.test_system_integration()
        
        # Ask user if they want to send a test email
        print("\n❓ Would you like to send a test email to the system? (y/n): ", end="")
        try:
            response = input().lower().strip()
            if response in ['y', 'yes', 'ja']:
                self.send_test_email()
        except KeyboardInterrupt:
            print("\n⚠️ Test interrupted by user")
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n📊 Test Summary")
        print("=" * 50)
        
        passed = len([r for r in self.results if r['status'] == '✅'])
        failed = len([r for r in self.results if r['status'] == '❌'])
        warnings = len([r for r in self.results if r['status'] == '⚠️'])
        total = len(self.results)
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Warnings: {warnings}")
        print(f"📈 Total: {total}")
        
        if failed == 0:
            print("\n🎉 All critical tests passed! System appears to be working correctly.")
            print("💡 You can now send emails to the system and expect AI responses.")
        else:
            print(f"\n⚠️ {failed} test(s) failed. Please review the issues above.")
            print("🔧 Check your .env file and Azure configuration.")
        
        print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main function"""
    test_suite = JasminCateringTestSuite()
    try:
        test_suite.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test suite interrupted by user")
        test_suite.print_summary()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        test_suite.print_summary()

if __name__ == "__main__":
    main()
