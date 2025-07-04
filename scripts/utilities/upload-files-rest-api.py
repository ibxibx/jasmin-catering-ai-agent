#!/usr/bin/env python3
"""
Upload knowledge files to vector store using REST API
"""

import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

VECTOR_STORE_ID = "vs_xDbEaqnBNUtJ70P7GoNgY1qD"
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
API_VERSION = "2024-05-01-preview"

def upload_file_to_openai(file_path, filename):
    """Upload a file to OpenAI Files API"""
    url = f"{ENDPOINT}/openai/files?api-version={API_VERSION}"
    
    headers = {
        "api-key": API_KEY
    }
    
    try:
        with open(file_path, 'rb') as f:
            files = {
                'file': (filename, f, 'text/plain'),
                'purpose': (None, 'assistants')
            }
            
            response = requests.post(url, headers=headers, files=files)
            
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Upload failed for {filename}: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception uploading {filename}: {str(e)}")
        return None

def add_file_to_vector_store(file_id, filename):
    """Add a file to the vector store"""
    url = f"{ENDPOINT}/openai/vector_stores/{VECTOR_STORE_ID}/files?api-version={API_VERSION}"
    
    headers = {
        "api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    data = {
        "file_id": file_id
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to add {filename} to vector store: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception adding {filename} to vector store: {str(e)}")
        return None

def list_vector_store_files():
    """List files currently in the vector store"""
    url = f"{ENDPOINT}/openai/vector_stores/{VECTOR_STORE_ID}/files?api-version={API_VERSION}"
    
    headers = {
        "api-key": API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to list vector store files: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Exception listing files: {str(e)}")
        return None

def main():
    """Upload all knowledge files"""
    print("📤 Uploading Knowledge Files to Vector Store")
    print("=" * 50)
    print(f"Vector Store ID: {VECTOR_STORE_ID}")
    print("")
    
    # Check current files in vector store
    print("📋 Current files in vector store:")
    current_files = list_vector_store_files()
    if current_files and current_files.get('data'):
        for file_info in current_files['data']:
            print(f"   - {file_info.get('id')} (Status: {file_info.get('status')})")
    else:
        print("   No files currently in vector store")
    
    print("")
    
    # Define knowledge files to upload
    documents_path = Path(__file__).parent / "deployments" / "documents"
    knowledge_files = [
        ("catering-brief.md", "Geschäftsprozess und System-Anforderungen"),
        ("business-conditions.md", "Geschäftsbedingungen und Preisstruktur"),
        ("vegetarian-offer-template.md", "Vorlage für vegetarische Angebote"),
        ("response-examples.md", "Beispiele für professionelle Antworten"),
        ("email-template.md", "Email-Vorlagen und Kommunikationsstandards"),
        ("jasmin_catering_prompt.md", "Agent-Anweisungen und RAG-Kontext")
    ]
    
    uploaded_files = []
    
    for filename, description in knowledge_files:
        file_path = documents_path / filename
        
        if not file_path.exists():
            print(f"⚠️  File not found: {filename}")
            continue
        
        print(f"📄 Processing {filename}...")
        
        # Step 1: Upload file to OpenAI
        print(f"   1. Uploading to OpenAI Files...")
        file_result = upload_file_to_openai(file_path, filename)
        
        if not file_result:
            continue
            
        file_id = file_result['id']
        print(f"   ✅ File uploaded: {file_id}")
        
        # Step 2: Add to vector store
        print(f"   2. Adding to vector store...")
        vs_result = add_file_to_vector_store(file_id, filename)
        
        if vs_result:
            print(f"   ✅ Added to vector store: {filename}")
            uploaded_files.append({
                "filename": filename,
                "description": description,
                "file_id": file_id,
                "vector_store_file_id": vs_result.get('id')
            })
        else:
            print(f"   ❌ Failed to add {filename} to vector store")
        
        print("")
    
    # Update configuration
    if uploaded_files:
        print("💾 Updating configuration...")
        
        config_path = Path(__file__).parent / "agent-config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        config["vector_store_id"] = VECTOR_STORE_ID
        config["vector_store_name"] = "AssistantVectorStore_Jasmin"
        config["uploaded_files"] = uploaded_files
        config["knowledge_uploaded"] = True
        config["upload_date"] = "2025-07-02"
        config["upload_method"] = "REST API"
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuration updated")
        print("")
        print("🎉 Knowledge Upload Complete!")
        print(f"   Vector Store: {VECTOR_STORE_ID}")
        print(f"   Files Uploaded: {len(uploaded_files)}")
        print("")
        print("📋 Uploaded Files:")
        for file_info in uploaded_files:
            print(f"   - {file_info['filename']} ({file_info['file_id']})")
        print("")
        print("🤖 The AI Assistant now has access to all knowledge documents!")
        print("   Test it with: python main.py")
        
    else:
        print("❌ No files were uploaded successfully")

if __name__ == "__main__":
    main()