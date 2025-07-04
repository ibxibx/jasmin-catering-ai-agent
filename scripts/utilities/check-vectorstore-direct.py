#!/usr/bin/env python3
"""
Check vector store using direct API calls and different methods
"""

import os
import requests
import json
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

def check_with_rest_api():
    """Check vector stores using direct REST API"""
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    
    # Try different API versions
    api_versions = ["2024-05-01-preview", "2024-07-01-preview", "2024-08-01-preview"]
    
    for api_version in api_versions:
        try:
            url = f"{endpoint}/openai/vector_stores?api-version={api_version}"
            headers = {
                "api-key": api_key,
                "Content-Type": "application/json"
            }
            
            print(f"Trying API version {api_version}...")
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success with API version {api_version}")
                print(f"Found {len(data.get('data', []))} vector stores")
                
                for vs in data.get('data', []):
                    print(f"  - {vs.get('name', 'Unnamed')} (ID: {vs.get('id')})")
                
                return True, data.get('data', []), api_version
                
            elif response.status_code == 404:
                print(f"❌ API version {api_version}: Vector stores not found (404)")
            else:
                print(f"❌ API version {api_version}: Error {response.status_code}")
                
        except Exception as e:
            print(f"❌ API version {api_version}: Exception {str(e)}")
    
    return False, [], None

def check_with_openai_sdk():
    """Check with different OpenAI SDK configurations"""
    api_versions = ["2024-05-01-preview", "2024-07-01-preview", "2024-08-01-preview"]
    
    for api_version in api_versions:
        try:
            print(f"\nTrying OpenAI SDK with API version {api_version}...")
            
            client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_version=api_version
            )
            
            # Check what's available in beta
            print(f"Available in beta: {[attr for attr in dir(client.beta) if not attr.startswith('_')]}")
            
            if hasattr(client.beta, 'vector_stores'):
                vector_stores = client.beta.vector_stores.list()
                print(f"✅ Success! Found {len(vector_stores.data)} vector stores")
                
                for vs in vector_stores.data:
                    print(f"  - {vs.name} (ID: {vs.id})")
                    
                return True, vector_stores.data, client
                
        except Exception as e:
            print(f"❌ SDK API version {api_version}: {str(e)}")
    
    return False, [], None

def check_assistant_current_config():
    """Check the current assistant configuration"""
    try:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version="2024-05-01-preview"
        )
        
        # Load assistant ID
        config_path = "agent-config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        assistant_id = config["agent_id"]
        assistant = client.beta.assistants.retrieve(assistant_id)
        
        print(f"\n🤖 Current Assistant Configuration:")
        print(f"   ID: {assistant.id}")
        print(f"   Name: {assistant.name}")
        print(f"   Model: {assistant.model}")
        print(f"   Tools: {[tool.type for tool in assistant.tools]}")
        
        if hasattr(assistant, 'tool_resources') and assistant.tool_resources:
            print(f"   Tool Resources: {assistant.tool_resources}")
            if hasattr(assistant.tool_resources, 'file_search'):
                print(f"   File Search Config: {assistant.tool_resources.file_search}")
        else:
            print(f"   Tool Resources: None")
            
        return assistant
        
    except Exception as e:
        print(f"❌ Error checking assistant: {str(e)}")
        return None

def main():
    """Main execution"""
    print("🔍 Comprehensive Vector Store Check")
    print("=" * 50)
    
    # Method 1: Direct REST API
    print("\n1. Checking with REST API...")
    found_rest, stores_rest, api_version = check_with_rest_api()
    
    # Method 2: OpenAI SDK
    print("\n2. Checking with OpenAI SDK...")
    found_sdk, stores_sdk, client = check_with_openai_sdk()
    
    # Method 3: Check current assistant
    print("\n3. Checking current assistant configuration...")
    assistant = check_assistant_current_config()
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   REST API: {'✅ Available' if found_rest else '❌ Not available'}")
    print(f"   OpenAI SDK: {'✅ Available' if found_sdk else '❌ Not available'}")
    print(f"   Assistant: {'✅ Retrieved' if assistant else '❌ Error'}")
    
    if found_rest or found_sdk:
        stores = stores_rest if found_rest else stores_sdk
        jasmin_store = None
        
        for store in stores:
            store_name = store.get('name') if isinstance(store, dict) else store.name
            if store_name == "AssistantVectorStore_Jasmin":
                jasmin_store = store
                break
        
        if jasmin_store:
            store_id = jasmin_store.get('id') if isinstance(jasmin_store, dict) else jasmin_store.id
            print(f"\n🎯 Found AssistantVectorStore_Jasmin!")
            print(f"   ID: {store_id}")
            print(f"\n📝 Next step: Run upload script with this vector store ID")
        else:
            print(f"\n❌ AssistantVectorStore_Jasmin not found among {len(stores)} vector stores")
            print("Available vector stores:")
            for store in stores:
                store_name = store.get('name') if isinstance(store, dict) else store.name
                store_id = store.get('id') if isinstance(store, dict) else store.id
                print(f"   - {store_name} ({store_id})")
    else:
        print(f"\n❌ Vector stores API not accessible")
        print("This could mean:")
        print("1. Vector stores not available in Sweden Central yet")
        print("2. Different API endpoint needed")
        print("3. Vector store created through different method")

if __name__ == "__main__":
    main()