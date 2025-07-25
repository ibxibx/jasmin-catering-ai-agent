#!/usr/bin/env python3
"""
Direct Azure OpenAI Connection Test
Test the Azure OpenAI connection directly without using the assistant
"""

import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

def test_azure_openai_direct():
    """Test Azure OpenAI connection directly"""
    
    print("Testing Azure OpenAI Direct Connection")
    print("=" * 50)
    
    # Get credentials
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY") 
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
    
    print(f"Endpoint: {endpoint}")
    print(f"API Key: {api_key[:8]}..." if api_key else "None")
    print(f"Deployment: {deployment}")
    
    if not endpoint or not api_key:
        print("ERROR: Missing endpoint or API key")
        return False
    
    try:
        # Initialize client
        print("Initializing Azure OpenAI client...")
        client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version="2024-05-01-preview"
        )
        print("SUCCESS: Client initialized")
        
        # Test a simple completion
        print("Testing chat completion...")
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {
                    "role": "user", 
                    "content": "Hallo! Können Sie mir kurz antworten?"
                }
            ],
            max_tokens=100,
            temperature=0.3
        )
        
        if response and response.choices:
            message = response.choices[0].message.content
            print("SUCCESS: Chat completion working!")
            print(f"Response: {message}")
            return True
        else:
            print("ERROR: No response received")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_list_assistants():
    """Test listing assistants"""
    
    print("\nTesting Assistant Listing")
    print("=" * 30)
    
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    
    try:
        client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version="2024-05-01-preview"
        )
        
        assistants = client.beta.assistants.list()
        print(f"Found {len(assistants.data)} assistants:")
        
        for assistant in assistants.data:
            print(f"  - {assistant.id}: {assistant.name}")
            
        return len(assistants.data) > 0
        
    except Exception as e:
        print(f"ERROR listing assistants: {e}")
        return False

if __name__ == "__main__":
    print("Azure OpenAI Direct Connection Test")
    print("=" * 60)
    
    # Test direct connection
    direct_success = test_azure_openai_direct()
    
    # Test assistant listing
    assistant_success = test_list_assistants()
    
    print("\n" + "=" * 60)
    print("RESULTS:")
    print(f"Direct OpenAI: {'SUCCESS' if direct_success else 'FAILED'}")
    print(f"Assistant API: {'SUCCESS' if assistant_success else 'FAILED'}")
    
    if direct_success:
        print("\nGOOD NEWS: Azure OpenAI is working!")
        print("The basic chat completion is functional.")
        if not assistant_success:
            print("However, assistants may need to be recreated.")
    else:
        print("\nISSUE: Azure OpenAI connection failed")
        print("Check endpoint and API key configuration.")
