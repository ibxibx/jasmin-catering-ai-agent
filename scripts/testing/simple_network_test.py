#!/usr/bin/env python3
"""
Simple network test to replace main.py temporarily
"""

import socket
import ssl
import imaplib
import os
import sys
from datetime import datetime

def simple_network_test():
    """Simple test that can replace main.py temporarily"""
    
    print(f"🔍 Simple Container Apps Network Test")
    print(f"=" * 40)
    print(f"🕐 {datetime.now()}")
    print(f"🏃 Environment: Container Apps")
    
    # Test 1: DNS Resolution
    print(f"\n🔍 Testing DNS...")
    try:
        ip = socket.gethostbyname("imap.web.de")
        print(f"✅ imap.web.de -> {ip}")
    except Exception as e:
        print(f"❌ DNS failed: {e}")
        return False
    
    # Test 2: Port connectivity
    print(f"\n🔌 Testing port 993...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex(("imap.web.de", 993))
        sock.close()
        if result == 0:
            print(f"✅ Port 993 reachable")
        else:
            print(f"❌ Port 993 blocked")
            return False
    except Exception as e:
        print(f"❌ Port test failed: {e}")
        return False
    
    # Test 3: SSL
    print(f"\n🔐 Testing SSL...")
    try:
        context = ssl.create_default_context()
        with socket.create_connection(("imap.web.de", 993), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname="imap.web.de") as ssock:
                print(f"✅ SSL works: {ssock.version()}")
    except Exception as e:
        print(f"❌ SSL failed: {e}")
        return False
    
    # Test 4: IMAP Authentication
    print(f"\n🔑 Testing IMAP auth...")
    email_addr = os.getenv('FROM_EMAIL_ADDRESS')
    password = os.getenv('WEBDE_APP_PASSWORD')
    
    if not email_addr or not password:
        print(f"❌ Missing credentials")
        print(f"   FROM_EMAIL_ADDRESS: {email_addr}")
        print(f"   WEBDE_APP_PASSWORD: {'***' if password else 'NOT SET'}")
        return False
    
    try:
        mail = imaplib.IMAP4_SSL("imap.web.de", 993)
        mail.login(email_addr, password)
        mail.select('inbox')
        
        # Quick email count
        status, messages = mail.search(None, 'ALL')
        if status == 'OK':
            count = len(messages[0].split()) if messages[0] else 0
            print(f"✅ IMAP works: {count} emails")
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"❌ IMAP auth failed: {e}")
        return False
    
    print(f"\n🎉 ALL NETWORK TESTS PASSED!")
    print(f"📧 Container can reach email services")
    return True

if __name__ == "__main__":
    success = simple_network_test()
    sys.exit(0 if success else 1)