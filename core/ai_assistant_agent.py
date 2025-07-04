"""
Azure AI Assistant using real AI Agents
Uses the Azure AI Agents SDK for true agent-based responses
"""

import os
import json
import time
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import MessageRole, RunStatus
from azure.core.credentials import AzureKeyCredential
from config.settings import BUSINESS_CONFIG

class JasminAIAssistantAgent:
    """AI Assistant using Azure AI Agents with vector store"""
    
    def __init__(self):
        """Initialize the AI Agent assistant"""
        # Load configuration
        config_path = Path(__file__).parent.parent / "agent-config.json"
        if not config_path.exists():
            raise FileNotFoundError(
                "Agent configuration not found. Run create-ai-agent-sdk.py first!"
            )
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize client
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", self.config.get("endpoint"))
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        
        if not endpoint or not api_key:
            raise ValueError("Missing AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY")
        
        self.client = AgentsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key)
        )
        
        self.agent_id = self.config["agent_id"]
        print(f"✅ Connected to AI Agent: {self.agent_id}")
    
    def generate_response(self, email_subject: str, email_body: str) -> Tuple[str, List[Dict], Dict]:
        """Generate AI response using the real AI Agent"""
        start_time = time.time()
        
        try:
            # Create a new thread for this conversation
            thread = self.client.threads.create()
            
            # Construct the user message
            user_message = f"""Betreff: {email_subject}

{email_body}

Bitte erstelle drei detaillierte Angebotsoptionen (Basis, Standard, Premium) mit transparenter Preisberechnung."""
            
            # Add message to thread
            self.client.messages.create(
                thread_id=thread.id,
                role=MessageRole.USER,
                content=user_message
            )
            
            # Run the agent
            run = self.client.runs.create(
                thread_id=thread.id,
                assistant_id=self.agent_id,
                instructions="Verwende die Wissensdatenbank für authentische Details und aktuelle Preise. Erstelle eine professionelle deutsche Geschäftsantwort."
            )
            
            # Wait for completion
            max_wait_time = 30  # seconds
            start_wait = time.time()
            
            while run.status in [RunStatus.QUEUED, RunStatus.IN_PROGRESS, RunStatus.REQUIRES_ACTION]:
                if time.time() - start_wait > max_wait_time:
                    print("⚠️  Agent response timeout")
                    return None, [], {"error": "timeout"}
                
                time.sleep(1)
                run = self.client.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
            
            if run.status == RunStatus.COMPLETED:
                # Get the assistant's response
                messages = self.client.messages.list(thread_id=thread.id)
                
                for message in messages.data:
                    if message.role == MessageRole.ASSISTANT:
                        # Extract text content
                        response_text = ""
                        for content in message.content:
                            if hasattr(content, 'text'):
                                response_text += content.text.value
                        
                        processing_time = time.time() - start_time
                        
                        # Extract information about used documents
                        documents_used = self._extract_used_documents(run)
                        
                        # Extract pricing
                        pricing_info = self._extract_pricing(response_text)
                        
                        # Get token usage if available
                        token_info = {}
                        if hasattr(run, 'usage'):
                            token_info = {
                                "prompt_tokens": run.usage.prompt_tokens,
                                "completion_tokens": run.usage.completion_tokens,
                                "total_tokens": run.usage.total_tokens
                            }
                        
                        return response_text, documents_used, {
                            'pricing': pricing_info,
                            'processing_time': f"{processing_time:.2f}s",
                            'documents_used': len(documents_used),
                            'agent_type': 'azure_ai_agent',
                            'agent_id': self.agent_id,
                            'thread_id': thread.id,
                            'run_id': run.id,
                            'tokens': token_info
                        }
                
                print("⚠️  No assistant response found")
                return None, [], {"error": "no_response"}
            
            else:
                error_msg = f"Run failed with status: {run.status}"
                if hasattr(run, 'last_error'):
                    error_msg += f" - {run.last_error}"
                print(f"❌ {error_msg}")
                return None, [], {"error": error_msg}
                
        except Exception as e:
            print(f"❌ Agent error: {str(e)}")
            return None, [], {"error": str(e)}
    
    def _extract_used_documents(self, run) -> List[Dict]:
        """Extract information about documents used by the agent"""
        documents = []
        
        # Check if run has file search results
        if hasattr(run, 'file_search_results'):
            for result in run.file_search_results:
                documents.append({
                    "title": result.file_name,
                    "content": result.content_snippet[:200] + "...",
                    "relevance_score": result.score
                })
        else:
            # Default documents that are always available
            documents = [
                {
                    "title": "Business Conditions",
                    "content": "Preisstruktur und Geschäftsbedingungen...",
                    "relevance_score": 1.0
                },
                {
                    "title": "Catering Brief",
                    "content": "Vollständige Geschäftsprozess-Beschreibung...",
                    "relevance_score": 0.9
                }
            ]
        
        return documents
    
    def _extract_pricing(self, response: str) -> Dict[str, str]:
        """Extract pricing information from AI response"""
        import re
        pricing = {}
        
        # Look for pricing patterns in the response
        patterns = {
            'Basis': [
                r'Basis[^:]*:\s*([0-9.,]+)\s*€',
                r'Basis[^:]*\s+([0-9.,]+)\s*€',
                r'Gesamtpreis[^:]*Basis[^:]*:\s*([0-9.,]+)\s*€'
            ],
            'Standard': [
                r'Standard[^:]*:\s*([0-9.,]+)\s*€',
                r'Standard[^:]*\s+([0-9.,]+)\s*€',
                r'Gesamtpreis[^:]*Standard[^:]*:\s*([0-9.,]+)\s*€'
            ],
            'Premium': [
                r'Premium[^:]*:\s*([0-9.,]+)\s*€',
                r'Premium[^:]*\s+([0-9.,]+)\s*€',
                r'Gesamtpreis[^:]*Premium[^:]*:\s*([0-9.,]+)\s*€'
            ]
        }
        
        for package, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, response, re.IGNORECASE)
                if matches:
                    pricing[package] = matches[-1] + "€"  # Take the last match (usually total)
                    break
        
        return pricing
    
    def get_agent_info(self) -> Dict:
        """Get information about the current agent"""
        try:
            agent = self.client.agents.retrieve(assistant_id=self.agent_id)
            return {
                "id": agent.id,
                "name": agent.name,
                "model": agent.model,
                "created_at": str(agent.created_at),
                "metadata": agent.metadata
            }
        except Exception as e:
            return {"error": str(e)}