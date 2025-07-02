#!/usr/bin/env python3
"""
Main application for Jasmin Catering AI Agent
Processes emails with AI + RAG + Slack notifications
"""

import time
from datetime import datetime
from core.email_processor import EmailProcessor
from core.ai_assistant import JasminAIAssistant
from core.slack_notifier import SlackNotifier
from config.settings import BUSINESS_CONFIG


class JasminCateringApp:
    """Main application class"""
    
    def __init__(self):
        self.email_processor = EmailProcessor()
        self.ai_assistant = JasminAIAssistant()
        self.slack = SlackNotifier()
        
    def run(self, test_mode: bool = False):
        """Run the email processing workflow"""
        print("\n🚀 Jasmin Catering AI Agent")
        print("=" * 60)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🏢 {BUSINESS_CONFIG['name']}")
        print(f"📍 {BUSINESS_CONFIG['location']}")
        print("=" * 60)
        
        # Log startup
        self.slack.log("🚀 Jasmin Catering AI Agent Started", "info", {
            "mode": "Test" if test_mode else "Production",
            "components": ["Email Processor", "AI Assistant", "RAG System", "Slack Notifier"]
        })
        
        # Process emails
        processed_count = 0
        error_count = 0
        
        try:
            # Fetch emails
            print("\n📧 Fetching catering emails...")
            emails = self.email_processor.fetch_catering_emails(limit=5)
            
            if not emails:
                print("No catering emails found.")
                self.slack.log("No catering emails to process", "info")
                return
            
            print(f"Found {len(emails)} catering emails to process\n")
            self.slack.log(f"📬 Found {len(emails)} catering emails", "info")
            
            # Process each email
            for i, email_data in enumerate(emails, 1):
                print(f"\n{'='*60}")
                print(f"Processing {i}/{len(emails)}: {email_data['subject']}")
                
                try:
                    # Post email to Slack
                    self.slack.post_email_request(email_data)
                    
                    # Generate AI response with RAG
                    print("🤖 Generating AI response with RAG...")
                    response, documents, info = self.ai_assistant.generate_response(
                        email_data['subject'],
                        email_data['body']
                    )
                    
                    if response:
                        # Send email response
                        print("📤 Sending response...")
                        success = self.email_processor.send_response(
                            self.email_processor.email_address,
                            email_data['subject'],
                            response,
                            documents
                        )
                        
                        if success:
                            processed_count += 1
                            print(f"✅ Response sent successfully")
                            print(f"📚 Used {len(documents)} RAG documents")
                            print(f"💰 Pricing: {info.get('pricing', {})}")
                            
                            # Post to Slack with full response
                            self.slack.post_ai_response(email_data['subject'], info, response)
                        else:
                            error_count += 1
                            print("❌ Failed to send response")
                            self.slack.log(f"Failed to send response for: {email_data['subject']}", "error")
                    else:
                        error_count += 1
                        print("❌ Failed to generate AI response")
                        # Post error to Slack with error info
                        error_info = {"error": "AI response generation failed", "documents_used": 0, "processing_time": "N/A"}
                        self.slack.post_ai_response(email_data['subject'], error_info)
                        self.slack.log(f"AI generation failed for: {email_data['subject']}", "error")
                        
                except Exception as e:
                    error_count += 1
                    print(f"❌ Error processing email: {e}")
                    self.slack.log(f"Email processing error", "error", {"error": str(e)})
            
            # Summary
            print(f"\n{'='*60}")
            print(f"✅ Processing Complete!")
            print(f"📊 Processed: {processed_count}/{len(emails)} emails")
            if error_count > 0:
                print(f"⚠️  Errors: {error_count}")
            
            # Log summary to Slack
            self.slack.log("📊 Processing Complete", "success", {
                "total_emails": len(emails),
                "processed": processed_count,
                "errors": error_count,
                "success_rate": f"{(processed_count/len(emails)*100):.0f}%"
            })
            
        except Exception as e:
            print(f"\n❌ Fatal error: {e}")
            self.slack.log("Fatal error in main application", "error", {"error": str(e)})


def main():
    """Entry point"""
    app = JasminCateringApp()
    app.run(test_mode=True)


if __name__ == "__main__":
    main()