#!/usr/bin/env python3
"""
Create Azure AI Agent using the official Python SDK
Based on: https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents-readme
"""

import os
import json
import asyncio
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    MessageRole,
    RunStatus
)
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

# Load environment variables
load_dotenv()

# Configuration
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
DOCUMENTS_PATH = Path(__file__).parent / "deployments" / "documents"

class JasminCateringAgentManager:
    """Manages the Jasmin Catering AI Agent"""
    
    def __init__(self):
        """Initialize the agent manager"""
        if not ENDPOINT or not API_KEY:
            raise ValueError("Missing AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY")
        
        # Initialize client
        self.client = AgentsClient(
            endpoint=ENDPOINT,
            credential=AzureKeyCredential(API_KEY)
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
    
    def create_vector_store(self):
        """Create a vector store for knowledge documents"""
        print("\n📚 Creating vector store...")
        
        vector_store = self.client.vector_stores.create(
            file_ids=[],  # We'll add files after uploading
            name="Jasmin Catering Knowledge Base",
            metadata={
                "description": "Catering knowledge documents",
                "created_by": "jasmin-catering-agent"
            }
        )
        
        print(f"✅ Vector store created: {vector_store.id}")
        return vector_store
    
    def upload_knowledge_files(self, vector_store_id: str) -> List[str]:
        """Upload knowledge documents to the agent"""
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
                        uploaded_file = self.client.files.create(
                            file=f,
                            purpose="assistants"
                        )
                    
                    # Add to vector store
                    self.client.vector_store_files.create(
                        vector_store_id=vector_store_id,
                        file_id=uploaded_file.id
                    )
                    
                    uploaded_file_ids.append(uploaded_file.id)
                    print(f"  ✅ Uploaded: {filename} (ID: {uploaded_file.id})")
                    
                except Exception as e:
                    print(f"  ❌ Failed to upload {filename}: {str(e)}")
            else:
                print(f"  ⚠️  File not found: {filename}")
        
        return uploaded_file_ids
    
    def create_agent(self):
        """Create the Jasmin Catering AI Agent"""
        print("\n🤖 Creating Jasmin Catering AI Agent...")
        
        # Read instructions
        instructions = self.read_prompt_file()
        
        # Create vector store
        vector_store = self.create_vector_store()
        
        # Upload knowledge files
        file_ids = self.upload_knowledge_files(vector_store.id)
        
        # Create agent with file search tool
        agent = self.client.agents.create(
            model="gpt-4o",
            name="Jasmin Catering Agent",
            description="Professional catering assistant for Jasmin Catering Berlin",
            instructions=instructions,
            tools=[{"type": "file_search"}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store.id]
                }
            },
            temperature=0.3,
            metadata={
                "created_by": "jasmin-catering-ai-agent",
                "version": "2.0",
                "includes_rag": "true",
                "knowledge_files": len(file_ids)
            }
        )
        
        print(f"✅ Agent created successfully!")
        print(f"   ID: {agent.id}")
        print(f"   Name: {agent.name}")
        print(f"   Model: {agent.model}")
        print(f"   Vector Store: {vector_store.id}")
        print(f"   Knowledge Files: {len(file_ids)}")
        
        # Save configuration
        self.save_agent_config(agent, vector_store.id, file_ids)
        
        return agent
    
    def save_agent_config(self, agent, vector_store_id: str, file_ids: List[str]):
        """Save agent configuration to file"""
        config = {
            "agent_id": agent.id,
            "agent_name": agent.name,
            "model": agent.model,
            "vector_store_id": vector_store_id,
            "file_ids": file_ids,
            "endpoint": ENDPOINT,
            "created_at": str(agent.created_at),
            "metadata": agent.metadata
        }
        
        config_path = Path(__file__).parent / "agent-config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n💾 Configuration saved to: {config_path}")
    
    def test_agent(self, agent_id: str):
        """Test the agent with a sample query"""
        print("\n🧪 Testing agent with sample query...")
        
        try:
            # Create thread
            thread = self.client.threads.create()
            print(f"📝 Created thread: {thread.id}")
            
            # Add message
            message = self.client.messages.create(
                thread_id=thread.id,
                role=MessageRole.USER,
                content="Ich möchte ein Catering für eine Hochzeit mit 100 Gästen buchen. Die Feier ist im Juni in Berlin. Können Sie mir bitte drei Angebotsoptionen zusenden?"
            )
            print(f"💬 Added user message")
            
            # Run agent
            run = self.client.runs.create(
                thread_id=thread.id,
                assistant_id=agent_id
            )
            print(f"🏃 Started run: {run.id}")
            
            # Wait for completion
            print("⏳ Waiting for response...")
            while run.status in [RunStatus.QUEUED, RunStatus.IN_PROGRESS, RunStatus.REQUIRES_ACTION]:
                import time
                time.sleep(2)
                run = self.client.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                print(f"   Status: {run.status}")
            
            if run.status == RunStatus.COMPLETED:
                # Get response
                messages = self.client.messages.list(thread_id=thread.id)
                
                print("\n✅ Agent Response:")
                print("=" * 80)
                
                for message in messages.data:
                    if message.role == MessageRole.ASSISTANT:
                        for content in message.content:
                            if hasattr(content, 'text'):
                                print(content.text.value)
                        break
                
                print("=" * 80)
                
                # Show usage
                if hasattr(run, 'usage'):
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
    
    def list_existing_agents(self):
        """List all existing agents"""
        print("\n📋 Listing existing agents...")
        try:
            agents = self.client.agents.list()
            if agents.data:
                for agent in agents.data:
                    print(f"  - {agent.name} (ID: {agent.id})")
            else:
                print("  No agents found")
        except Exception as e:
            print(f"  Error listing agents: {e}")

def main():
    """Main execution"""
    print("🚀 Jasmin Catering AI Agent Creator")
    print("=" * 50)
    
    try:
        # Initialize manager
        manager = JasminCateringAgentManager()
        
        # List existing agents
        manager.list_existing_agents()
        
        # Create new agent
        agent = manager.create_agent()
        
        # Test the agent
        if agent:
            manager.test_agent(agent.id)
            
            print("\n📝 Next Steps:")
            print("1. Update core/ai_assistant_agent.py to use this agent")
            print("2. Deploy the updated application")
            print("3. Monitor agent performance in Azure")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("1. Ensure Azure OpenAI resource supports Assistants API")
        print("2. Check AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in .env")
        print("3. Verify the resource is in a supported region")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()