#!/usr/bin/env python3
"""
Create Azure AI Agent with Knowledge Store in Azure AI Foundry
This script creates an agent and uploads knowledge documents
"""

import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("AZURE_AI_API_KEY")
ENDPOINT = "https://jasmin-catering-resource.openai.azure.com"
DOCUMENTS_PATH = Path(__file__).parent / "deployments" / "documents"

def read_prompt_file() -> str:
    """Read the jasmin_catering_prompt.md file"""
    prompt_path = DOCUMENTS_PATH / "jasmin_catering_prompt.md"
    print(f"📖 Reading prompt from: {prompt_path}")
    
    with open(prompt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"✅ Prompt loaded ({len(content)} characters)")
    return content

def upload_knowledge_files(client, agent_id):
    """Upload knowledge documents to the agent"""
    print("\n📤 Uploading knowledge documents...")
    
    # Create vector store first
    print("📚 Creating vector store...")
    vector_store = client.vector_stores.create(
        name="Jasmin Catering Knowledge Base",
        metadata={
            "agent_id": agent_id,
            "purpose": "catering-knowledge"
        }
    )
    print(f"✅ Vector store created: {vector_store.id}")
    
    # Define the knowledge files to upload
    knowledge_files = [
        ("catering-brief.md", "Geschäftsprozess und System-Anforderungen"),
        ("business-conditions.md", "Geschäftsbedingungen und Preisstruktur"),
        ("vegetarian-offer-template.md", "Vorlage für vegetarische Angebote"),
        ("response-examples.md", "Beispiele für professionelle Antworten"),
        ("email-template.md", "Email-Vorlagen und Kommunikationsstandards")
    ]
    
    uploaded_files = []
    
    for filename, description in knowledge_files:
        file_path = DOCUMENTS_PATH / filename
        if file_path.exists():
            try:
                print(f"  📄 Uploading {filename}...")
                
                # Upload file
                with open(file_path, 'rb') as f:
                    file_response = client.files.create(
                        file=f,
                        purpose="assistants"
                    )
                
                # Add file to vector store
                client.vector_store_files.create(
                    vector_store_id=vector_store.id,
                    file_id=file_response.id
                )
                
                uploaded_files.append(file_response.id)
                print(f"  ✅ Uploaded: {filename} (ID: {file_response.id})")
                
            except Exception as e:
                print(f"  ❌ Failed to upload {filename}: {str(e)}")
        else:
            print(f"  ⚠️  File not found: {filename}")
    
    return vector_store.id, uploaded_files

def create_ai_agent():
    """Create Azure AI Agent with knowledge store"""
    print("🚀 Creating Azure AI Agent with Knowledge Store")
    print("=" * 50)
    
    try:
        # Initialize client with API key auth
        if not API_KEY:
            print("❌ AZURE_AI_API_KEY not found in environment")
            return None, None
            
        # For AgentsClient, we need to pass the API key differently
        client = AgentsClient(
            endpoint=ENDPOINT,
            credential=AzureKeyCredential(API_KEY),
            api_version="2024-02-01"
        )
        print(f"✅ Connected to Azure AI Service at {ENDPOINT}")
        
        # Read prompt
        prompt = read_prompt_file()
        
        # Create agent with file search capability
        print("\n🤖 Creating AI Agent...")
        agent = client.create_agent(
            model="gpt-4o",
            name="Jasmin Catering Agent",
            instructions=prompt,
            tools=[{"type": "file_search"}],
            temperature=0.3,
            metadata={
                "created_by": "jasmin-catering-ai-agent",
                "purpose": "catering-email-responses",
                "includes_rag": "true"
            }
        )
        
        print(f"✅ Agent created successfully!")
        print(f"   ID: {agent.id}")
        print(f"   Name: {agent.name}")
        
        # Upload knowledge files and create vector store
        vector_store_id, uploaded_files = upload_knowledge_files(client, agent.id)
        
        # Update agent to use the vector store
        print("\n🔗 Linking vector store to agent...")
        client.update_agent(
            assistant_id=agent.id,
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store_id]
                }
            }
        )
        print("✅ Vector store linked to agent")
        
        # Save agent configuration
        config = {
            "agent_id": agent.id,
            "vector_store_id": vector_store_id,
            "uploaded_files": uploaded_files,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model": "gpt-4o",
            "endpoint": ENDPOINT
        }
        
        config_path = Path(__file__).parent / "agent-config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n💾 Configuration saved to: {config_path}")
        print("\n✨ Agent setup complete!")
        print(f"\n📋 Agent Details:")
        print(f"   - Agent ID: {agent.id}")
        print(f"   - Vector Store ID: {vector_store_id}")
        print(f"   - Knowledge Files: {len(uploaded_files)}")
        print(f"   - Model: gpt-4o")
        
        return agent.id, vector_store_id
        
    except Exception as e:
        print(f"\n❌ Error creating agent: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("1. Ensure AZURE_AI_API_KEY is set correctly")
        print("2. Verify you have access to Azure AI services")
        print("3. Check that agents API is enabled on your resource")
        print(f"\nDetailed error: {type(e).__name__}: {str(e)}")
        return None, None

def test_agent(agent_id):
    """Test the created agent with a sample query"""
    print("\n🧪 Testing agent with sample query...")
    
    try:
        if not API_KEY:
            print("❌ AZURE_AI_API_KEY not found")
            return
            
        client = AgentsClient(
            endpoint=ENDPOINT,
            credential=AzureKeyCredential(API_KEY),
            api_version="2024-02-01"
        )
        
        # Create a thread
        thread = client.threads.create()
        
        # Add a test message
        message = client.messages.create(
            thread_id=thread.id,
            role="user",
            content="Ich möchte ein Catering für 50 Personen für eine Hochzeit buchen. Was können Sie mir anbieten?"
        )
        
        # Run the agent
        run = client.runs.create(
            thread_id=thread.id,
            assistant_id=agent_id
        )
        
        # Wait for completion
        print("⏳ Waiting for response...")
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)
            run = client.runs.retrieve(thread_id=thread.id, run_id=run.id)
        
        if run.status == "completed":
            # Get messages
            messages = client.messages.list(thread_id=thread.id)
            for msg in messages.data:
                if msg.role == "assistant":
                    print("\n✅ Agent Response:")
                    print("-" * 50)
                    if msg.content:
                        for content in msg.content:
                            if hasattr(content, 'text'):
                                print(content.text.value)
                    print("-" * 50)
                    break
        else:
            print(f"❌ Run failed with status: {run.status}")
            if hasattr(run, 'last_error'):
                print(f"Error: {run.last_error}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

def main():
    """Main execution"""
    agent_id, vector_store_id = create_ai_agent()
    
    if agent_id:
        # Test the agent
        test_agent(agent_id)
        
        print("\n📝 Next Steps:")
        print("1. Update ai_assistant.py to use this agent")
        print("2. Deploy the updated application")
        print("3. Test email processing with the new agent")
        
if __name__ == "__main__":
    main()