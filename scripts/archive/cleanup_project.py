#!/usr/bin/env python3
"""
Clean up and restructure the Jasmin Catering project
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """Remove unnecessary files and organize project structure"""
    
    # Files to keep (core functionality)
    keep_files = {
        # Configuration
        '.env',
        '.gitignore',
        'requirements.txt',
        
        # Documentation
        'README.md',
        'PRICING_EXPLANATION.md',
        'SLACK_INTEGRATION_GUIDE.md',
        'RAG_PROOF_REPORT.md',
        
        # Core modules
        'config.py',
        'slack_notifier.py',
        'email_processor.py',
        'ai_assistant.py',
        
        # Knowledge base
        'knowledge-base/documents/business-info.md',
        'knowledge-base/documents/menu-offerings.md',
        'knowledge-base/documents/pricing-structure.md',
        'knowledge-base/documents/service-policies.md',
        
        # RAG system
        'rag-system/document-indexer.py',
        
        # Main application
        'main.py',
        
        # Utilities
        'utils/send_test_emails.py',
        'utils/test_slack.py',
        'utils/setup_oauth.py',
    }
    
    # Directories to clean
    cleanup_dirs = [
        'deployments/archive',
        '__pycache__',
        '.pytest_cache'
    ]
    
    # Patterns to remove
    remove_patterns = [
        'test-*.py',
        'enhanced-*.py',
        'simple-*.py',
        'basic-*.py',
        '*-old.py',
        '*-backup.py',
        '*.log',
        '*.txt'  # except requirements.txt
    ]
    
    print("🧹 Starting project cleanup...")
    
    # Create new directory structure
    new_dirs = ['config', 'core', 'utils', 'docs', 'tests']
    for dir_name in new_dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"📁 Created directory: {dir_name}")
    
    # Remove unnecessary directories
    for dir_path in cleanup_dirs:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"🗑️  Removed directory: {dir_path}")
    
    # Count files before cleanup
    all_files = list(Path('.').rglob('*'))
    file_count_before = len([f for f in all_files if f.is_file()])
    
    print(f"\n📊 Files before cleanup: {file_count_before}")
    
    # Remove files matching patterns
    removed_count = 0
    for pattern in remove_patterns:
        for file_path in Path('.').rglob(pattern):
            if file_path.is_file() and file_path.name != 'requirements.txt':
                try:
                    file_path.unlink()
                    removed_count += 1
                    print(f"🗑️  Removed: {file_path}")
                except Exception as e:
                    print(f"⚠️  Could not remove {file_path}: {e}")
    
    print(f"\n✅ Cleanup complete!")
    print(f"📊 Files removed: {removed_count}")
    
    # Count files after cleanup
    all_files = list(Path('.').rglob('*'))
    file_count_after = len([f for f in all_files if f.is_file()])
    print(f"📊 Files after cleanup: {file_count_after}")
    print(f"💾 Space saved: {file_count_before - file_count_after} files")

if __name__ == "__main__":
    cleanup_project()