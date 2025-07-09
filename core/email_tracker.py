"""
Email tracking to prevent duplicate processing
Uses Azure Table Storage to track processed emails
"""

import os
import json
from datetime import datetime, timedelta
from azure.data.tables import TableServiceClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
import hashlib


class EmailTracker:
    """Track processed emails to prevent duplicates"""
    
    def __init__(self):
        # Use Azure Storage connection string from environment
        connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        if connection_string:
            self.table_service = TableServiceClient.from_connection_string(connection_string)
            self.table_name = "ProcessedEmails"
            self._ensure_table_exists()
        else:
            # Fallback to local file tracking if no Azure Storage
            print("⚠️ No Azure Storage configured, using local file tracking")
            self.use_file_tracking = True
            self.tracking_file = "/tmp/processed_emails.json"
            self._load_tracked_emails()
    
    def _ensure_table_exists(self):
        """Create table if it doesn't exist"""
        try:
            self.table_service.create_table(self.table_name)
            print(f"✅ Created table: {self.table_name}")
        except ResourceExistsError:
            pass
    
    def _load_tracked_emails(self):
        """Load tracked emails from file (fallback method)"""
        self.tracked_emails = {}
        if os.path.exists(self.tracking_file):
            try:
                with open(self.tracking_file, 'r') as f:
                    data = json.load(f)
                    # Clean up old entries (older than 7 days)
                    cutoff = (datetime.now() - timedelta(days=7)).isoformat()
                    self.tracked_emails = {
                        k: v for k, v in data.items() 
                        if v.get('processed_at', '') > cutoff
                    }
            except:
                self.tracked_emails = {}
    
    def _save_tracked_emails(self):
        """Save tracked emails to file (fallback method)"""
        try:
            with open(self.tracking_file, 'w') as f:
                json.dump(self.tracked_emails, f)
        except Exception as e:
            print(f"⚠️ Could not save tracking file: {e}")
    
    def _generate_email_id(self, email_data: dict) -> str:
        """Generate unique ID for email based on content"""
        # Create hash from subject + from + date
        content = f"{email_data.get('subject', '')}{email_data.get('from', '')}{email_data.get('date', '')}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def is_processed(self, email_data: dict) -> bool:
        """Check if email has been processed"""
        email_id = self._generate_email_id(email_data)
        
        if hasattr(self, 'use_file_tracking'):
            # File-based tracking
            return email_id in self.tracked_emails
        else:
            # Azure Table Storage
            try:
                table_client = self.table_service.get_table_client(self.table_name)
                entity = table_client.get_entity(
                    partition_key="emails",
                    row_key=email_id
                )
                return True
            except ResourceNotFoundError:
                return False
            except Exception as e:
                print(f"⚠️ Error checking email status: {e}")
                return False
    
    def mark_processed(self, email_data: dict):
        """Mark email as processed"""
        email_id = self._generate_email_id(email_data)
        
        if hasattr(self, 'use_file_tracking'):
            # File-based tracking
            self.tracked_emails[email_id] = {
                'processed_at': datetime.now().isoformat(),
                'subject': email_data.get('subject', ''),
                'from': email_data.get('from', '')
            }
            self._save_tracked_emails()
        else:
            # Azure Table Storage
            try:
                table_client = self.table_service.get_table_client(self.table_name)
                entity = {
                    'PartitionKey': 'emails',
                    'RowKey': email_id,
                    'ProcessedAt': datetime.now().isoformat(),
                    'Subject': email_data.get('subject', ''),
                    'From': email_data.get('from', ''),
                    'Date': email_data.get('date', '')
                }
                table_client.create_entity(entity)
                print(f"✅ Marked email as processed: {email_data.get('subject', '')}")
            except ResourceExistsError:
                # Already processed
                pass
            except Exception as e:
                print(f"⚠️ Error marking email as processed: {e}")
    
    def cleanup_old_entries(self, days: int = 7):
        """Remove entries older than specified days"""
        cutoff = datetime.now() - timedelta(days=days)
        
        if hasattr(self, 'use_file_tracking'):
            # File-based cleanup
            self._load_tracked_emails()
            self._save_tracked_emails()
        else:
            # Azure Table Storage cleanup
            try:
                table_client = self.table_service.get_table_client(self.table_name)
                entities = table_client.query_entities(
                    filter=f"ProcessedAt lt '{cutoff.isoformat()}'"
                )
                for entity in entities:
                    table_client.delete_entity(
                        partition_key=entity['PartitionKey'],
                        row_key=entity['RowKey']
                    )
            except Exception as e:
                print(f"⚠️ Error cleaning up old entries: {e}")