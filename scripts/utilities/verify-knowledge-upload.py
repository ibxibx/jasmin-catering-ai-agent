#!/usr/bin/env python3
"""
Verify that knowledge files have been uploaded successfully
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

VECTOR_STORE_ID = "vs_xDbEaqnBNUtJ70P7GoNgY1qD"
ASSISTANT_ID = "asst_UHTUDffJEyLQ6qexElqOopac"
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
API_VERSION = "2024-05-01-preview"

def check_vector_store_files():
    """Check files in the vector store"""
    url = f"{ENDPOINT}/openai/vector_stores/{VECTOR_STORE_ID}/files?api-version={API_VERSION}"
    
    headers = {"api-key": API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        else:
            print(f"❌ Error checking vector store: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return []

def check_assistant_config():
    """Check assistant configuration"""
    url = f"{ENDPOINT}/openai/assistants/{ASSISTANT_ID}?api-version={API_VERSION}"
    
    headers = {"api-key": API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error checking assistant: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def main():
    """Verify the knowledge upload"""
    print("🔍 Verifying Knowledge Upload")
    print("=" * 40)
    
    # Check vector store files
    print("1. Checking vector store files...")
    files = check_vector_store_files()
    
    if files:
        print(f"✅ Found {len(files)} files in vector store:")
        for file_info in files:
            status = file_info.get('status', 'unknown')
            file_id = file_info.get('id', 'unknown')
            print(f"   - {file_id} (Status: {status})")
    else:
        print("❌ No files found in vector store")
    
    # Check assistant configuration
    print(f"\n2. Checking assistant configuration...")
    assistant = check_assistant_config()
    
    if assistant:
        print(f"✅ Assistant retrieved:")
        print(f"   Name: {assistant.get('name')}")
        print(f"   Model: {assistant.get('model')}")
        
        tool_resources = assistant.get('tool_resources', {})
        file_search = tool_resources.get('file_search', {})
        vector_store_ids = file_search.get('vector_store_ids', [])
        
        if vector_store_ids:
            print(f"   Vector Stores: {vector_store_ids}")
            if VECTOR_STORE_ID in vector_store_ids:
                print(f"   ✅ Assistant is linked to our vector store!")
            else:
                print(f"   ❌ Assistant not linked to our vector store")
        else:
            print(f"   ❌ No vector stores linked to assistant")
    else:
        print("❌ Could not retrieve assistant")
    
    # Check local configuration
    print(f"\n3. Checking local configuration...")
    try:
        with open('agent-config.json', 'r') as f:
            config = json.load(f)
        
        if config.get('knowledge_uploaded'):
            uploaded_files = config.get('uploaded_files', [])
            print(f"✅ Local config shows {len(uploaded_files)} files uploaded")
            print(f"   Upload date: {config.get('upload_date')}")
            print(f"   Vector store: {config.get('vector_store_id')}")
        else:
            print("❌ Local config shows no upload")
            
    except Exception as e:
        print(f"❌ Error reading config: {str(e)}")
    
    # Summary
    print(f"\n📊 Summary:")
    files_count = len(files) if files else 0
    assistant_linked = assistant and VECTOR_STORE_ID in assistant.get('tool_resources', {}).get('file_search', {}).get('vector_store_ids', [])
    
    print(f"   Vector Store Files: {files_count}/6")
    print(f"   Assistant Linked: {'Yes' if assistant_linked else 'No'}")
    
    if files_count == 6 and assistant_linked:
        print(f"\n🎉 Knowledge Upload Verification: SUCCESS!")
        print(f"   All 6 knowledge files are uploaded and accessible")
        print(f"   The AI Assistant can now use RAG with the knowledge base")
        print(f"\n📝 Next steps:")
        print(f"   - Test: python main.py")
        print(f"   - Deploy: az acr build --registry jasmincateringregistry --image jasmin-catering-ai:latest .")
    else:
        print(f"\n⚠️  Knowledge Upload Verification: INCOMPLETE")
        print(f"   Some files may not be uploaded or assistant not properly linked")

if __name__ == "__main__":
    main()