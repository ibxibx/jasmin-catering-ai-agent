#!/usr/bin/env python3
"""
Test networking connectivity from Container Apps to email services
"""

import socket
import ssl
import imaplib
import smtplib
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_dns_resolution():
    """Test DNS resolution for email servers"""
    print("🔍 Testing DNS Resolution...")
    
    hosts = [
        "imap.web.de",
        "smtp.web.de", 
        "web.de",
        "google.com"  # Control test
    ]
    
    for host in hosts:
        try:
            ip = socket.gethostbyname(host)
            print(f"✅ {host} -> {ip}")
        except Exception as e:
            print(f"❌ {host} -> DNS Error: {e}")

def test_port_connectivity():
    """Test port connectivity to email servers"""
    print("\n🔌 Testing Port Connectivity...")
    
    connections = [
        ("imap.web.de", 993, "IMAP SSL"),
        ("imap.web.de", 143, "IMAP"),
        ("smtp.web.de", 587, "SMTP STARTTLS"),
        ("smtp.web.de", 465, "SMTP SSL"),
        ("smtp.web.de", 25, "SMTP"),
        ("google.com", 80, "HTTP Control")
    ]
    
    for host, port, description in connections:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ {host}:{port} ({description}) - Connected")
            else:
                print(f"❌ {host}:{port} ({description}) - Connection failed")
        except Exception as e:
            print(f"❌ {host}:{port} ({description}) - Error: {e}")

def test_ssl_connectivity():
    """Test SSL connectivity to IMAP server"""
    print("\n🔐 Testing SSL/TLS Connectivity...")
    
    try:
        context = ssl.create_default_context()
        with socket.create_connection(("imap.web.de", 993), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname="imap.web.de") as ssock:
                print(f"✅ SSL connection to imap.web.de:993 successful")
                print(f"   SSL Version: {ssock.version()}")
                print(f"   Cipher: {ssock.cipher()}")
    except Exception as e:
        print(f"❌ SSL connection failed: {e}")

def test_imap_authentication():
    """Test IMAP authentication"""
    print("\n🔑 Testing IMAP Authentication...")
    
    email_address = os.getenv('FROM_EMAIL_ADDRESS', 'matthias.buchhorn@web.de')
    password = os.getenv('WEBDE_APP_PASSWORD')
    
    if not password:
        print("❌ WEBDE_APP_PASSWORD environment variable not set")
        return False
    
    try:
        print(f"🔌 Connecting to IMAP server...")
        mail = imaplib.IMAP4_SSL("imap.web.de", 993)
        print(f"✅ IMAP connection established")
        
        print(f"🔐 Authenticating with {email_address}...")
        mail.login(email_address, password)
        print(f"✅ IMAP authentication successful")
        
        print(f"📁 Selecting inbox...")
        mail.select('inbox')
        print(f"✅ Inbox selected")
        
        print(f"📊 Getting inbox status...")
        status, count = mail.search(None, 'ALL')
        if status == 'OK':
            total_emails = len(count[0].split()) if count[0] else 0
            print(f"✅ Found {total_emails} total emails in inbox")
        
        mail.close()
        mail.logout()
        print(f"✅ IMAP connection closed successfully")
        return True
        
    except Exception as e:
        print(f"❌ IMAP test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_smtp_connectivity():
    """Test SMTP connectivity"""
    print("\n📤 Testing SMTP Connectivity...")
    
    email_address = os.getenv('FROM_EMAIL_ADDRESS', 'matthias.buchhorn@web.de')
    password = os.getenv('WEBDE_APP_PASSWORD')
    
    if not password:
        print("❌ WEBDE_APP_PASSWORD environment variable not set")
        return False
    
    try:
        print(f"🔌 Connecting to SMTP server...")
        server = smtplib.SMTP("smtp.web.de", 587)
        print(f"✅ SMTP connection established")
        
        print(f"🔐 Starting TLS...")
        server.starttls()
        print(f"✅ TLS started")
        
        print(f"🔑 Authenticating...")
        server.login(email_address, password)
        print(f"✅ SMTP authentication successful")
        
        server.quit()
        print(f"✅ SMTP connection closed")
        return True
        
    except Exception as e:
        print(f"❌ SMTP test failed: {e}")
        return False

def test_environment_variables():
    """Test environment variables"""
    print("\n🌍 Testing Environment Variables...")
    
    required_vars = [
        'FROM_EMAIL_ADDRESS',
        'WEBDE_APP_PASSWORD', 
        'WEBDE_EMAIL_ALIAS',
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_OPENAI_API_KEY'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var or 'KEY' in var:
                print(f"✅ {var}: {'*' * len(value)}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")

def main():
    """Run all networking tests"""
    print(f"🔍 Container Apps Networking Test")
    print(f"=" * 50)
    print(f"🕐 Test time: {datetime.now()}")
    print(f"🐍 Python version: {sys.version}")
    print(f"🏃 Running from: Container Apps" if os.getenv('AZURE_CONTAINER_APPS') else "Local Machine")
    
    test_environment_variables()
    test_dns_resolution()
    test_port_connectivity()
    test_ssl_connectivity()
    
    imap_success = test_imap_authentication()
    smtp_success = test_smtp_connectivity()
    
    print(f"\n📊 Test Summary:")
    print(f"=" * 30)
    print(f"IMAP Connection: {'✅ PASS' if imap_success else '❌ FAIL'}")
    print(f"SMTP Connection: {'✅ PASS' if smtp_success else '❌ FAIL'}")
    
    if imap_success and smtp_success:
        print(f"\n🎉 All email connectivity tests PASSED!")
        print(f"📧 Container can connect to email services")
    else:
        print(f"\n❌ Email connectivity tests FAILED!")
        print(f"🚫 Container cannot connect to email services")
        
    return imap_success and smtp_success

if __name__ == "__main__":
    main()