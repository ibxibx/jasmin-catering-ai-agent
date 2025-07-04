#!/usr/bin/env python3
"""
Create Azure AI Agent using OpenAI SDK
Azure OpenAI Assistants API is compatible with OpenAI's SDK
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

# Configuration
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
API_VERSION = "2024-05-01-preview"  # Latest version with Assistants
DOCUMENTS_PATH = Path(__file__).parent / "deployments" / "documents"

class JasminCateringAgentManager:
    """Manages the Jasmin Catering AI Agent using OpenAI SDK"""
    
    def __init__(self):
        """Initialize the agent manager"""
        if not ENDPOINT or not API_KEY:
            raise ValueError("Missing AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY")
        
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            api_key=API_KEY,
            api_version=API_VERSION,
            azure_endpoint=ENDPOINT
        )
        print(f"✅ Connected to: {ENDPOINT}")
    
    def read_prompt_file(self) -> str:
        """Read the agent instructions from prompt file"""
        prompt_path = DOCUMENTS_PATH / "jasmin_catering_prompt.md"
        print(f"📖 Reading prompt from: {prompt_path}")
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ Prompt loaded ({len(content)} characters)")
        return content
    
    def create_agent(self):
        """Create the Jasmin Catering AI Agent"""
        print("\n🤖 Creating Jasmin Catering AI Agent...")
        
        # Read instructions
        instructions = self.read_prompt_file()
        
        # Create assistant (agent)
        try:
            assistant = self.client.beta.assistants.create(
                model="gpt-4o",
                name="Jasmin Catering Agent",
                description="Professional catering assistant for Jasmin Catering Berlin",
                instructions=instructions,
                tools=[{"type": "file_search"}],
                temperature=0.3,
                metadata={
                    "created_by": "jasmin-catering-ai-agent",
                    "version": "2.0",
                    "includes_rag": "true"
                }
            )
            
            print(f"✅ Assistant created successfully!")
            print(f"   ID: {assistant.id}")
            print(f"   Name: {assistant.name}")
            print(f"   Model: {assistant.model}")
            
            return assistant
            
        except Exception as e:
            print(f"❌ Error creating assistant: {str(e)}")
            return None
    
    def create_vector_store_and_upload_files(self, assistant_id):
        """Create vector store and upload knowledge files"""
        print("\n📚 Creating vector store...")
        
        # Create vector store
        vector_store = self.client.beta.vector_stores.create(
            name="Jasmin Catering Knowledge Base",
            metadata={
                "assistant_id": assistant_id,
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
            ("email-template.md", "Email-Vorlagen und Kommunikationsstandards"),
            ("jasmin_catering_prompt.md", "Agent-Anweisungen und RAG-Kontext")
        ]
        
        uploaded_file_ids = []
        
        for filename, description in knowledge_files:
            file_path = DOCUMENTS_PATH / filename
            if file_path.exists():
                try:
                    print(f"  📄 Uploading {filename}...")
                    
                    # Upload file
                    with open(file_path, 'rb') as f:
                        file = self.client.files.create(
                            file=f,
                            purpose="assistants"
                        )
                    
                    # Add to vector store
                    self.client.beta.vector_stores.files.create(
                        vector_store_id=vector_store.id,
                        file_id=file.id
                    )
                    
                    uploaded_file_ids.append(file.id)
                    print(f"  ✅ Uploaded: {filename} (ID: {file.id})")
                    
                except Exception as e:
                    print(f"  ❌ Failed to upload {filename}: {str(e)}")
            else:
                print(f"  ⚠️  File not found: {filename}")
        
        # Update assistant to use vector store
        print("\n🔗 Linking vector store to assistant...")
        self.client.beta.assistants.update(
            assistant_id=assistant_id,
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store.id]
                }
            }
        )
        print("✅ Vector store linked to assistant")
        
        return vector_store.id, uploaded_file_ids
    
    def test_assistant(self, assistant_id):
        """Test the assistant with a sample query"""
        print("\n🧪 Testing assistant with sample query...")
        
        try:
            # Create thread
            thread = self.client.beta.threads.create()
            print(f"📝 Created thread: {thread.id}")
            
            # Add message
            message = self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content="Ich möchte ein Catering für eine Hochzeit mit 100 Gästen buchen. Die Feier ist im Juni in Berlin. Können Sie mir bitte drei Angebotsoptionen zusenden?"
            )
            print(f"💬 Added user message")
            
            # Run assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant_id
            )
            print(f"🏃 Started run: {run.id}")
            
            # Wait for completion
            print("⏳ Waiting for response...")
            while run.status in ["queued", "in_progress", "requires_action"]:
                time.sleep(2)
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                print(f"   Status: {run.status}")
            
            if run.status == "completed":
                # Get response
                messages = self.client.beta.threads.messages.list(thread_id=thread.id)
                
                print("\n✅ Assistant Response:")
                print("=" * 80)
                
                for message in messages.data:
                    if message.role == "assistant":
                        for content in message.content:
                            if hasattr(content, 'text'):
                                print(content.text.value)
                        break
                
                print("=" * 80)
                
                # Show token usage if available
                if hasattr(run, 'usage') and run.usage:
                    print(f"\n📊 Token Usage:")
                    print(f"   Prompt: {run.usage.prompt_tokens}")
                    print(f"   Completion: {run.usage.completion_tokens}")
                    print(f"   Total: {run.usage.total_tokens}")
            else:
                print(f"❌ Run failed with status: {run.status}")
                if hasattr(run, 'last_error'):
                    print(f"   Error: {run.last_error}")
                    
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def save_agent_config(self, assistant, vector_store_id, file_ids):
        """Save agent configuration to file"""
        config = {
            "agent_id": assistant.id,
            "agent_name": assistant.name,
            "model": assistant.model,
            "vector_store_id": vector_store_id,
            "file_ids": file_ids,
            "endpoint": ENDPOINT,
            "api_version": API_VERSION,
            "created_at": str(assistant.created_at),
            "metadata": assistant.metadata
        }
        
        config_path = Path(__file__).parent / "agent-config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n💾 Configuration saved to: {config_path}")
    
    def list_existing_assistants(self):
        """List all existing assistants"""
        print("\n📋 Listing existing assistants...")
        try:
            assistants = self.client.beta.assistants.list()
            if assistants.data:
                for assistant in assistants.data:
                    print(f"  - {assistant.name} (ID: {assistant.id})")
            else:
                print("  No assistants found")
        except Exception as e:
            print(f"  Error listing assistants: {e}")

def main():
    """Main execution"""
    print("🚀 Jasmin Catering AI Agent Creator (OpenAI SDK)")
    print("=" * 50)
    
    try:
        # Initialize manager
        manager = JasminCateringAgentManager()
        
        # List existing assistants
        manager.list_existing_assistants()
        
        # Create new assistant
        assistant = manager.create_agent()
        
        if assistant:
            # Create vector store and upload files
            vector_store_id, file_ids = manager.create_vector_store_and_upload_files(assistant.id)
            
            # Save configuration
            manager.save_agent_config(assistant, vector_store_id, file_ids)
            
            # Test the assistant
            manager.test_assistant(assistant.id)
            
            print("\n📝 Next Steps:")
            print("1. Update main.py to use ai_assistant_agent.py")
            print("2. Deploy the updated application")
            print("3. Monitor agent performance in Azure")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("1. Ensure Azure OpenAI resource supports Assistants API")
        print("2. Check AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in .env")
        print("3. Verify the resource is in Sweden Central region")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()