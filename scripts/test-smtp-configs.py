#!/usr/bin/env python3
"""
Test different SMTP configurations for web.de/matthias.buchhorn@web.de
"""

import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

def test_smtp_config(smtp_server, port, use_tls=True):
    """Test SMTP configuration"""
    
    sender = os.getenv('FROM_EMAIL_ADDRESS', 'matthias.buchhorn@web.de')
    password = os.getenv('FROM_EMAIL_PASSWORD')
    
    if not password:
        print("❌ No password found in environment")
        return False
    
    print(f"🧪 Testing: {smtp_server}:{port} (TLS: {use_tls})")
    
    try:
        if use_tls:
            server = smtplib.SMTP(smtp_server, port)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(smtp_server, port)
        
        print(f"   📡 Connected to {smtp_server}")
        
        server.login(sender, password)
        print(f"   ✅ Authentication successful for {sender}")
        
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"   ❌ Authentication failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False

def main():
    print("🔍 Testing SMTP Configurations for matthias.buchhorn@web.de")
    print("=" * 60)
    print()
    
    # Different SMTP configurations to try
    configs = [
        ('smtp.web.de', 587, True),
        ('smtp.web.de', 465, False),
        ('smtp.1und1.de', 587, True),
        ('smtp.1und1.de', 465, False),
        ('smtp.gmx.net', 587, True),
        ('smtp.gmx.net', 465, False),
    ]
    
    for smtp_server, port, use_tls in configs:
        if test_smtp_config(smtp_server, port, use_tls):
            print(f"🎉 Working configuration found: {smtp_server}:{port}")
            break
        print()
    else:
        print("❌ No working SMTP configuration found")
        print()
        print("💡 Suggestions:")
        print("1. Verify the app password is correct")
        print("2. Check if 2FA is enabled and app password is required")
        print("3. Try generating a new app password")

if __name__ == "__main__":
    main()