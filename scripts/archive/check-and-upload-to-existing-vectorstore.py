#!/usr/bin/env python3
"""
Check for existing vector store and upload knowledge files
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

def check_existing_vector_stores():
    """Check for existing vector stores"""
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version="2024-05-01-preview"
    )
    
    try:
        print("🔍 Checking for existing vector stores...")
        
        # Try to list vector stores
        if hasattr(client.beta, 'vector_stores'):
            vector_stores = client.beta.vector_stores.list()
            
            print(f"Found {len(vector_stores.data)} vector stores:")
            for vs in vector_stores.data:
                print(f"  - {vs.name} (ID: {vs.id})")
                
            # Look for the specific vector store
            jasmin_store = None
            for vs in vector_stores.data:
                if vs.name == "AssistantVectorStore_Jasmin":
                    jasmin_store = vs
                    break
                    
            if jasmin_store:
                print(f"\n✅ Found AssistantVectorStore_Jasmin: {jasmin_store.id}")
                return True, client, jasmin_store.id
            else:
                print("\n❌ AssistantVectorStore_Jasmin not found")
                return False, client, None
                
        else:
            print("❌ Vector stores API not available")
            return False, None, None
            
    except Exception as e:
        print(f"❌ Error accessing vector stores: {str(e)}")
        return False, None, None

def upload_files_to_vector_store(client, vector_store_id):
    """Upload knowledge files to the existing vector store"""
    print(f"\n📤 Uploading files to vector store: {vector_store_id}")
    
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
        if file_path.exists():
            try:
                print(f"  📄 Uploading {filename}...")
                
                # Upload file to OpenAI
                with open(file_path, 'rb') as f:
                    file = client.files.create(
                        file=f,
                        purpose="assistants"
                    )
                
                # Add file to vector store
                client.beta.vector_stores.files.create(
                    vector_store_id=vector_store_id,
                    file_id=file.id
                )
                
                uploaded_files.append({
                    "file_id": file.id,
                    "filename": filename,
                    "description": description
                })
                print(f"  ✅ Uploaded: {filename} (ID: {file.id})")
                
            except Exception as e:
                print(f"  ❌ Failed to upload {filename}: {str(e)}")
        else:
            print(f"  ⚠️  File not found: {filename}")
    
    return uploaded_files

def update_assistant_with_vector_store(client, assistant_id, vector_store_id):
    """Update the assistant to use the vector store"""
    print(f"\n🔗 Linking vector store to assistant...")
    
    try:
        # Get current assistant configuration
        assistant = client.beta.assistants.retrieve(assistant_id)
        print(f"Current assistant: {assistant.name}")
        
        # Update assistant to use vector store
        updated_assistant = client.beta.assistants.update(
            assistant_id=assistant_id,
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store_id]
                }
            }
        )
        
        print("✅ Assistant updated with vector store")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update assistant: {str(e)}")
        return False

def update_config_file(vector_store_id, uploaded_files):
    """Update the agent configuration file"""
    config_path = Path(__file__).parent / "agent-config.json"
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        config["vector_store_id"] = vector_store_id
        config["vector_store_name"] = "AssistantVectorStore_Jasmin"
        config["uploaded_files"] = uploaded_files
        config["knowledge_uploaded"] = True
        config["upload_date"] = "2025-07-02"
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuration updated: {config_path}")
        
    except Exception as e:
        print(f"❌ Failed to update config: {str(e)}")

def main():
    """Main execution"""
    print("🚀 Checking for AssistantVectorStore_Jasmin")
    print("=" * 50)
    
    # Load assistant config
    config_path = Path(__file__).parent / "agent-config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    assistant_id = config["agent_id"]
    print(f"Assistant ID: {assistant_id}")
    
    # Check for existing vector store
    found, client, vector_store_id = check_existing_vector_stores()
    
    if found and vector_store_id:
        print(f"\n📚 Proceeding with upload to: {vector_store_id}")
        
        # Upload files
        uploaded_files = upload_files_to_vector_store(client, vector_store_id)
        
        if uploaded_files:
            print(f"\n📋 Upload Summary:")
            print(f"   Vector Store: {vector_store_id}")
            print(f"   Files Uploaded: {len(uploaded_files)}")
            
            for file_info in uploaded_files:
                print(f"   - {file_info['filename']} ({file_info['file_id']})")
            
            # Update assistant
            if update_assistant_with_vector_store(client, assistant_id, vector_store_id):
                # Update config
                update_config_file(vector_store_id, uploaded_files)
                
                print(f"\n🎉 Knowledge upload complete!")
                print(f"The assistant now has access to all {len(uploaded_files)} knowledge documents.")
                
            else:
                print(f"\n⚠️  Files uploaded but assistant update failed")
        else:
            print(f"\n❌ No files were uploaded successfully")
            
    else:
        print(f"\n❌ Could not find or access AssistantVectorStore_Jasmin")
        print("Please ensure:")
        print("1. The vector store exists and is named exactly 'AssistantVectorStore_Jasmin'")
        print("2. You have access to the Azure OpenAI resource")
        print("3. Vector stores API is available in your region")

if __name__ == "__main__":
    main()