#!/usr/bin/env python3
"""
Test web.de SMTP authentication for both email addresses
Based on web.de SMTP documentation
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_webde_smtp(email_address, password, test_send=False):
    """
    Test web.de SMTP authentication
    
    According to web.de documentation:
    - SMTP Server: smtp.web.de
    - Port: 587 (TLS) or 465 (SSL)
    - Authentication: Required
    - Encryption: STARTTLS (port 587) or SSL/TLS (port 465)
    """
    
    print(f"🧪 Testing SMTP for: {email_address}")
    print(f"🔑 Using password: {password[:4]}...{password[-4:]}")
    
    # Test both port configurations
    configs = [
        ('smtp.web.de', 587, 'STARTTLS'),
        ('smtp.web.de', 465, 'SSL/TLS')
    ]
    
    for smtp_server, port, encryption in configs:
        print(f"\n📡 Testing {smtp_server}:{port} ({encryption})")
        
        try:
            if port == 587:
                # STARTTLS configuration
                server = smtplib.SMTP(smtp_server, port)
                server.starttls()
            else:
                # SSL/TLS configuration
                server = smtplib.SMTP_SSL(smtp_server, port)
            
            print(f"   ✅ Connected to {smtp_server}:{port}")
            
            # Test authentication
            server.login(email_address, password)
            print(f"   ✅ Authentication successful for {email_address}")
            
            if test_send:
                # Send a test email
                msg = MIMEMultipart()
                msg['From'] = email_address
                msg['To'] = "ma3u-test@email.de"  # Send to alias
                msg['Subject'] = f"Test Email from {email_address} - {datetime.now().strftime('%H:%M:%S')}"
                
                body = f"""Test Email

This is a test email sent from {email_address} using web.de SMTP.

Configuration used:
- Server: {smtp_server}
- Port: {port}
- Encryption: {encryption}
- Time: {datetime.now()}

Jasmin Catering AI Agent Test
"""
                msg.attach(MIMEText(body, 'plain'))
                
                server.send_message(msg)
                print(f"   ✅ Test email sent successfully!")
            
            server.quit()
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"   ❌ Authentication failed: {e}")
        except smtplib.SMTPException as e:
            print(f"   ❌ SMTP error: {e}")
        except Exception as e:
            print(f"   ❌ Connection error: {e}")
    
    return False

def main():
    print("🌐 Web.de SMTP Authentication Test")
    print("=" * 50)
    print("Testing both email addresses with new app password")
    print()
    
    # Get credentials from environment
    password = os.getenv('FROM_EMAIL_PASSWORD', os.getenv('WEBDE_APP_PASSWORD'))
    
    if not password:
        print("❌ Error: No password found in environment variables")
        print("Please ensure FROM_EMAIL_PASSWORD or WEBDE_APP_PASSWORD is set")
        return
    
    # Test both email addresses
    email_addresses = [
        "matthias.buchhorn@web.de",  # Main account
        "ma3u-test@email.de"        # Alias
    ]
    
    working_configs = []
    
    for email in email_addresses:
        print(f"\n{'='*60}")
        print(f"Testing: {email}")
        print('='*60)
        
        if test_webde_smtp(email, password, test_send=True):
            working_configs.append(email)
            print(f"\n🎉 SUCCESS: {email} authentication working!")
        else:
            print(f"\n❌ FAILED: {email} authentication failed")
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    
    if working_configs:
        print(f"✅ Working email addresses: {len(working_configs)}")
        for email in working_configs:
            print(f"   - {email}")
        print()
        print("📧 Test emails sent! Check ma3u-test@email.de inbox")
    else:
        print("❌ No working email configurations found")
        print()
        print("💡 Troubleshooting:")
        print("1. Verify the app password is correct")
        print("2. Check that 2FA is enabled in web.de settings")
        print("3. Ensure app passwords are enabled in security settings")
        print("4. Try generating a fresh app password")

if __name__ == "__main__":
    main()