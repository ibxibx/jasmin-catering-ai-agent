#!/usr/bin/env python3
"""
Automated deployment test script for GitHub Actions
Sends test email and verifies Container Apps Job processing
"""

import os
import sys
import time
import smtplib
import imaplib
import email
import json
import subprocess
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class DeploymentTester:
    def __init__(self):
        # Email configuration
        self.email_address = os.getenv('FROM_EMAIL_ADDRESS', 'matthias.buchhorn@web.de')
        self.password = os.getenv('WEBDE_APP_PASSWORD')
        self.test_alias = 'ma3u-test@email.de'
        
        # Azure configuration
        self.resource_group = os.getenv('AZURE_RESOURCE_GROUP', 'logicapp-jasmin-sweden_group')
        self.container_job = os.getenv('CONTAINER_APP_JOB', 'jasmin-email-processor')
        
        # Test configuration
        self.test_subject = f"🧪 CI/CD Test - Deployment Verification - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self.test_timeout = 300  # 5 minutes max wait time
        
    def send_test_email(self):
        """Send test catering inquiry email"""
        print(f"📧 Sending test email to {self.test_alias}...")
        
        try:
            # Create test email content
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = self.test_alias
            msg['Subject'] = self.test_subject
            
            body = f"""Hallo Jasmin Catering Team,

ich möchte gerne eine Catering-Anfrage für eine Hochzeitsfeier stellen.

Event Details:
- Datum: 15. September 2025
- Uhrzeit: 18:00 Uhr
- Anzahl Gäste: 85 Personen
- Location: Hochzeitssaal Berlin-Mitte
- Art: Hochzeitsfeier

Besondere Wünsche:
- Vegetarische Optionen für 15 Gäste
- Glutenfreie Alternativen für 3 Gäste
- Syrische Spezialitäten bevorzugt
- Getränkepaket inklusive

Könnten Sie mir bitte ein Angebot erstellen?

Vielen Dank!
Beste Grüße
CI/CD Test System

---
Test ID: {datetime.now().strftime('%Y%m%d-%H%M%S')}
Deployment Verification: GitHub Actions
"""
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Send email via SMTP
            server = smtplib.SMTP('smtp.web.de', 587)
            server.starttls()
            server.login(self.email_address, self.password)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Test email sent successfully")
            print(f"   📋 Subject: {self.test_subject}")
            print(f"   📬 To: {self.test_alias}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send test email: {e}")
            return False
    
    def trigger_container_job(self):
        """Trigger manual Container Apps Job execution"""
        print(f"🚀 Triggering Container Apps Job execution...")
        
        try:
            # Start the job
            cmd = [
                'az', 'containerapp', 'job', 'start',
                '--name', self.container_job,
                '--resource-group', self.resource_group,
                '--query', 'name',
                '-o', 'tsv'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                execution_name = result.stdout.strip()
                print(f"✅ Job triggered successfully: {execution_name}")
                return execution_name
            else:
                print(f"❌ Failed to trigger job: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Error triggering job: {e}")
            return None
    
    def wait_for_job_completion(self, execution_name, timeout=300):
        """Wait for Container Apps Job execution to complete"""
        print(f"⏳ Waiting for job execution to complete (max {timeout}s)...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check execution status
                cmd = [
                    'az', 'containerapp', 'job', 'execution', 'show',
                    '--name', self.container_job,
                    '--resource-group', self.resource_group,
                    '--job-execution-name', execution_name,
                    '--query', 'properties.status',
                    '-o', 'tsv'
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    status = result.stdout.strip()
                    print(f"   📊 Status: {status}")
                    
                    if status == 'Succeeded':
                        print(f"✅ Job execution completed successfully")
                        return True
                    elif status == 'Failed':
                        print(f"❌ Job execution failed")
                        return False
                    elif status in ['Running', 'Pending']:
                        time.sleep(10)  # Wait 10 seconds before checking again
                        continue
                
                time.sleep(10)
                
            except Exception as e:
                print(f"⚠️  Error checking job status: {e}")
                time.sleep(10)
        
        print(f"⏰ Timeout waiting for job completion")
        return False
    
    def get_job_logs(self, lines=50):
        """Get Container Apps Job logs"""
        print(f"📋 Retrieving job logs (last {lines} lines)...")
        
        try:
            cmd = [
                'az', 'containerapp', 'job', 'logs', 'show',
                '--name', self.container_job,
                '--resource-group', self.resource_group,
                '--container', self.container_job,
                '--follow', 'false',
                '--tail', str(lines)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logs = result.stdout
                print(f"📝 Job Logs:")
                print("-" * 60)
                print(logs)
                print("-" * 60)
                
                # Check if our test email was processed
                if self.test_subject in logs:
                    print(f"✅ Test email found in logs!")
                    return True, logs
                else:
                    print(f"❌ Test email NOT found in logs")
                    return False, logs
            else:
                print(f"❌ Failed to get logs: {result.stderr}")
                return False, ""
                
        except Exception as e:
            print(f"❌ Error getting logs: {e}")
            return False, ""
    
    def verify_email_processing(self):
        """Verify test email was processed by checking logs for specific patterns"""
        print(f"🔍 Verifying email processing...")
        
        success, logs = self.get_job_logs(100)
        
        if not success:
            return False
        
        # Check for key processing indicators
        indicators = [
            "Found",  # Found X catering emails
            "Processing",  # Processing X/Y emails
            "AI response",  # AI response generation
            "Response sent successfully",  # Email response sent
            "Processing Complete"  # Job completion
        ]
        
        found_indicators = []
        for indicator in indicators:
            if indicator.lower() in logs.lower():
                found_indicators.append(indicator)
        
        print(f"📊 Processing indicators found: {len(found_indicators)}/{len(indicators)}")
        for indicator in found_indicators:
            print(f"   ✅ {indicator}")
        
        # Consider successful if we found at least 3 indicators
        if len(found_indicators) >= 3:
            print(f"✅ Email processing verification PASSED")
            return True
        else:
            print(f"❌ Email processing verification FAILED")
            return False
    
    def generate_test_report(self, results):
        """Generate JSON test report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_subject": self.test_subject,
            "test_alias": self.test_alias,
            "container_job": self.container_job,
            "resource_group": self.resource_group,
            "results": results,
            "overall_success": all(results.values())
        }
        
        # Write report to file
        with open('deployment_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def run_full_test(self):
        """Run complete deployment test"""
        print(f"🧪 Starting Deployment Test")
        print(f"=" * 60)
        print(f"🕐 Test started at: {datetime.now()}")
        print(f"📧 Test email: {self.test_alias}")
        print(f"🎯 Container Job: {self.container_job}")
        print(f"📦 Resource Group: {self.resource_group}")
        print(f"=" * 60)
        
        results = {}
        
        # Step 1: Send test email
        print(f"\n📧 STEP 1: Send Test Email")
        results['email_sent'] = self.send_test_email()
        
        if not results['email_sent']:
            print(f"❌ Test failed at email sending step")
            return self.generate_test_report(results)
        
        # Step 2: Trigger job
        print(f"\n🚀 STEP 2: Trigger Container Job")
        execution_name = self.trigger_container_job()
        results['job_triggered'] = execution_name is not None
        
        if not results['job_triggered']:
            print(f"❌ Test failed at job trigger step")
            return self.generate_test_report(results)
        
        # Step 3: Wait for completion
        print(f"\n⏳ STEP 3: Wait for Job Completion")
        results['job_completed'] = self.wait_for_job_completion(execution_name)
        
        # Step 4: Verify processing (even if job didn't complete successfully)
        print(f"\n🔍 STEP 4: Verify Email Processing")
        results['email_processed'] = self.verify_email_processing()
        
        # Generate final report
        report = self.generate_test_report(results)
        
        # Print summary
        print(f"\n🎯 TEST SUMMARY")
        print(f"=" * 60)
        for step, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{step.replace('_', ' ').title()}: {status}")
        
        overall_success = report['overall_success']
        print(f"\nOverall Result: {'✅ SUCCESS' if overall_success else '❌ FAILURE'}")
        print(f"📊 Report saved: deployment_test_report.json")
        print(f"=" * 60)
        
        return report

def main():
    """Main test execution"""
    # Check required environment variables
    required_vars = ['WEBDE_APP_PASSWORD', 'FROM_EMAIL_ADDRESS']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        sys.exit(1)
    
    # Run test
    tester = DeploymentTester()
    report = tester.run_full_test()
    
    # Exit with appropriate code
    sys.exit(0 if report['overall_success'] else 1)

if __name__ == "__main__":
    main()