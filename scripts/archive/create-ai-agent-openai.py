#!/usr/bin/env python3
"""
Create Azure AI Agent using OpenAI SDK (Assistants API)
Azure AI Agents are compatible with OpenAI Assistants API
"""

import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("AZURE_AI_API_KEY")
ENDPOINT = "https://jasmin-catering-resource.cognitiveservices.azure.com"
DOCUMENTS_PATH = Path(__file__).parent / "deployments" / "documents"

def read_prompt_file() -> str:
    """Read the jasmin_catering_prompt.md file"""
    prompt_path = DOCUMENTS_PATH / "jasmin_catering_prompt.md"
    print(f"📖 Reading prompt from: {prompt_path}")
    
    with open(prompt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"✅ Prompt loaded ({len(content)} characters)")
    return content

def create_ai_agent_with_openai():
    """Create Azure AI Agent using OpenAI SDK"""
    print("🚀 Creating Azure AI Agent with OpenAI SDK")
    print("=" * 50)
    
    if not API_KEY:
        print("❌ AZURE_AI_API_KEY not found in environment")
        return None, None
    
    try:
        # Initialize OpenAI client for Azure
        client = AzureOpenAI(
            api_key=API_KEY,
            api_version="2024-02-01",
            azure_endpoint=ENDPOINT
        )
        print(f"✅ Connected to Azure OpenAI at {ENDPOINT}")
        
        # Read prompt
        prompt = read_prompt_file()
        
        # Create assistant (agent)
        print("\n🤖 Creating AI Assistant...")
        assistant = client.beta.assistants.create(
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
        
        print(f"✅ Assistant created successfully!")
        print(f"   ID: {assistant.id}")
        print(f"   Name: {assistant.name}")
        
        # Create vector store
        print("\n📚 Creating vector store...")
        vector_store = client.beta.vector_stores.create(
            name="Jasmin Catering Knowledge Base",
            metadata={
                "assistant_id": assistant.id,
                "purpose": "catering-knowledge"
            }
        )
        print(f"✅ Vector store created: {vector_store.id}")
        
        # Upload knowledge files
        print("\n📤 Uploading knowledge documents...")
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
                        file = client.files.create(
                            file=f,
                            purpose="assistants"
                        )
                    
                    # Add to vector store
                    client.beta.vector_stores.files.create(
                        vector_store_id=vector_store.id,
                        file_id=file.id
                    )
                    
                    uploaded_files.append(file.id)
                    print(f"  ✅ Uploaded: {filename} (ID: {file.id})")
                    
                except Exception as e:
                    print(f"  ❌ Failed to upload {filename}: {str(e)}")
            else:
                print(f"  ⚠️  File not found: {filename}")
        
        # Update assistant to use vector store
        print("\n🔗 Linking vector store to assistant...")
        client.beta.assistants.update(
            assistant_id=assistant.id,
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store.id]
                }
            }
        )
        print("✅ Vector store linked to assistant")
        
        # Save configuration
        config = {
            "agent_id": assistant.id,
            "vector_store_id": vector_store.id,
            "uploaded_files": uploaded_files,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model": "gpt-4o",
            "endpoint": ENDPOINT,
            "api_version": "2024-02-01"
        }
        
        config_path = Path(__file__).parent / "agent-config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n💾 Configuration saved to: {config_path}")
        print("\n✨ Agent setup complete!")
        print(f"\n📋 Agent Details:")
        print(f"   - Assistant ID: {assistant.id}")
        print(f"   - Vector Store ID: {vector_store.id}")
        print(f"   - Knowledge Files: {len(uploaded_files)}")
        print(f"   - Model: gpt-4o")
        
        return assistant.id, vector_store.id
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print(f"\nDetailed error: {type(e).__name__}: {str(e)}")
        return None, None

def test_assistant(assistant_id):
    """Test the assistant with a sample query"""
    print("\n🧪 Testing assistant with sample query...")
    
    if not API_KEY:
        print("❌ AZURE_AI_API_KEY not found")
        return
    
    try:
        client = AzureOpenAI(
            api_key=API_KEY,
            api_version="2024-02-01",
            azure_endpoint=ENDPOINT
        )
        
        # Create thread
        thread = client.beta.threads.create()
        
        # Add message
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content="Ich möchte ein Catering für 50 Personen für eine Hochzeit buchen. Was können Sie mir anbieten?"
        )
        
        # Run assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )
        
        # Wait for completion
        print("⏳ Waiting for response...")
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
        
        if run.status == "completed":
            # Get messages
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            for msg in messages.data:
                if msg.role == "assistant":
                    print("\n✅ Assistant Response:")
                    print("-" * 50)
                    for content in msg.content:
                        if hasattr(content, 'text'):
                            print(content.text.value)
                    print("-" * 50)
                    break
        else:
            print(f"❌ Run failed with status: {run.status}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

def main():
    """Main execution"""
    assistant_id, vector_store_id = create_ai_agent_with_openai()
    
    if assistant_id:
        test_assistant(assistant_id)
        
        print("\n📝 Next Steps:")
        print("1. Update ai_assistant.py to use this assistant")
        print("2. Deploy the updated application")
        print("3. Test email processing with the new assistant")

if __name__ == "__main__":
    main()