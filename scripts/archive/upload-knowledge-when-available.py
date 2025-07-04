#!/usr/bin/env python3
"""
Upload knowledge files to AI Agent vector store when API becomes available
Run this script periodically to check if vector stores are supported
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

def check_vector_store_availability():
    """Check if vector stores API is available"""
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version="2024-05-01-preview"
    )
    
    try:
        # Try to access vector_stores - will fail if not available
        if hasattr(client.beta, 'vector_stores'):
            print("✅ Vector stores API is available!")
            return True, client
        else:
            print("❌ Vector stores API not yet available")
            return False, None
    except Exception as e:
        print(f"❌ Vector stores API not available: {str(e)}")
        return False, None

def upload_knowledge_files(client, assistant_id):
    """Upload knowledge files to vector store"""
    print("\n📚 Creating vector store...")
    
    # Create vector store
    vector_store = client.beta.vector_stores.create(
        name="Jasmin Catering Knowledge Base",
        metadata={
            "assistant_id": assistant_id,
            "purpose": "catering-knowledge"
        }
    )
    print(f"✅ Vector store created: {vector_store.id}")
    
    # Upload files
    documents_path = Path(__file__).parent / "deployments" / "documents"
    knowledge_files = [
        "catering-brief.md",
        "business-conditions.md", 
        "vegetarian-offer-template.md",
        "response-examples.md",
        "email-template.md",
        "jasmin_catering_prompt.md"
    ]
    
    uploaded_files = []
    for filename in knowledge_files:
        file_path = documents_path / filename
        if file_path.exists():
            try:
                print(f"  📄 Uploading {filename}...")
                
                with open(file_path, 'rb') as f:
                    file = client.files.create(file=f, purpose="assistants")
                
                client.beta.vector_stores.files.create(
                    vector_store_id=vector_store.id,
                    file_id=file.id
                )
                
                uploaded_files.append(file.id)
                print(f"  ✅ Uploaded: {filename}")
                
            except Exception as e:
                print(f"  ❌ Failed to upload {filename}: {e}")
    
    # Update assistant to use vector store
    print("\n🔗 Linking vector store to assistant...")
    client.beta.assistants.update(
        assistant_id=assistant_id,
        tool_resources={
            "file_search": {
                "vector_store_ids": [vector_store.id]
            }
        }
    )
    
    # Update config file
    config_path = Path(__file__).parent / "agent-config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    config["vector_store_id"] = vector_store.id
    config["uploaded_files"] = uploaded_files
    config["knowledge_uploaded"] = True
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Knowledge base setup complete!")
    print(f"   Vector Store: {vector_store.id}")
    print(f"   Files: {len(uploaded_files)}")
    
    return vector_store.id

def main():
    """Check and upload if available"""
    print("🔍 Checking Vector Store Availability")
    print("=" * 40)
    
    # Load assistant config
    config_path = Path(__file__).parent / "agent-config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    assistant_id = config["agent_id"]
    print(f"Assistant ID: {assistant_id}")
    
    # Check if already uploaded
    if config.get("knowledge_uploaded"):
        print("✅ Knowledge files already uploaded!")
        print(f"Vector Store: {config.get('vector_store_id')}")
        return
    
    # Check API availability
    available, client = check_vector_store_availability()
    
    if available:
        try:
            vector_store_id = upload_knowledge_files(client, assistant_id)
            print(f"\n🎉 Knowledge upload complete!")
            print(f"The assistant now has access to all knowledge documents.")
        except Exception as e:
            print(f"\n❌ Upload failed: {str(e)}")
    else:
        print("\n⏳ Vector stores not yet available in Sweden Central")
        print("The assistant currently uses embedded knowledge in instructions.")
        print("Run this script again later to check availability.")

if __name__ == "__main__":
    main()