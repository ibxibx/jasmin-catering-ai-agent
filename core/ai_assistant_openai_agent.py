"""
Azure AI Assistant using OpenAI SDK with Assistants API
Uses the real Azure OpenAI Assistant we created
"""

import os
import json
import time
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from openai import AzureOpenAI
from config.settings import BUSINESS_CONFIG

class JasminAIAssistantOpenAI:
    """AI Assistant using Azure OpenAI Assistants API"""
    
    def __init__(self):
        """Initialize the AI Assistant"""
        # Load configuration
        config_path = Path(__file__).parent.parent / "agent-config.json"
        if not config_path.exists():
            raise FileNotFoundError(
                "Agent configuration not found. Run create-ai-agent-openai-sdk.py first!"
            )
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize client
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", self.config.get("endpoint"))
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        
        if not endpoint or not api_key:
            raise ValueError("Missing AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY")
        
        self.client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=self.config.get("api_version", "2024-05-01-preview")
        )
        
        self.assistant_id = self.config["agent_id"]
        print(f"Connected to AI Assistant: {self.assistant_id}")
    
    def generate_response(self, email_subject: str, email_body: str) -> Tuple[str, List[Dict], Dict]:
        """Generate AI response using the real Azure OpenAI Assistant"""
        start_time = time.time()
        
        try:
            # Create a new thread for this conversation
            thread = self.client.beta.threads.create()
            
            # Construct the user message
            user_message = f"""Betreff: {email_subject}

{email_body}

Bitte erstelle drei detaillierte Angebotsoptionen (Basis, Standard, Premium) mit transparenter Preisberechnung."""
            
            # Add message to thread
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_message
            )
            
            # Run the assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant_id,
                instructions="Verwende dein Wissen über Jasmin Catering für authentische Details und aktuelle Preise. Erstelle eine professionelle deutsche Geschäftsantwort mit drei Angebotsoptionen."
            )
            
            # Wait for completion
            max_wait_time = 30  # seconds
            start_wait = time.time()
            
            while run.status in ["queued", "in_progress", "requires_action"]:
                if time.time() - start_wait > max_wait_time:
                    print("⚠️  Assistant response timeout")
                    return None, [], {"error": "timeout"}
                
                time.sleep(1)
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
            
            if run.status == "completed":
                # Get the assistant's response
                messages = self.client.beta.threads.messages.list(thread_id=thread.id)
                
                for message in messages.data:
                    if message.role == "assistant":
                        # Extract text content
                        response_text = ""
                        for content in message.content:
                            if hasattr(content, 'text'):
                                response_text += content.text.value
                        
                        processing_time = time.time() - start_time
                        
                        # Extract information about used documents
                        documents_used = self._extract_used_documents(message)
                        
                        # Extract pricing
                        pricing_info = self._extract_pricing(response_text)
                        
                        # Get token usage if available
                        token_info = {}
                        if hasattr(run, 'usage') and run.usage:
                            token_info = {
                                "prompt_tokens": run.usage.prompt_tokens,
                                "completion_tokens": run.usage.completion_tokens,
                                "total_tokens": run.usage.total_tokens
                            }
                        
                        return response_text, documents_used, {
                            'pricing': pricing_info,
                            'processing_time': f"{processing_time:.2f}s",
                            'documents_used': len(documents_used),
                            'agent_type': 'azure_openai_assistant',
                            'assistant_id': self.assistant_id,
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
            print(f"❌ Assistant error: {str(e)}")
            return None, [], {"error": str(e)}
    
    def _extract_used_documents(self, message) -> List[Dict]:
        """Extract information about documents used by the assistant"""
        documents = []
        
        # Check if message has annotations (file citations)
        if hasattr(message, 'content'):
            for content in message.content:
                if hasattr(content, 'text') and hasattr(content.text, 'annotations'):
                    for annotation in content.text.annotations:
                        if hasattr(annotation, 'file_citation'):
                            documents.append({
                                "title": f"Document {annotation.file_citation.file_id}",
                                "content": annotation.text[:200] + "...",
                                "relevance_score": 1.0
                            })
        
        # If no documents found in annotations, return default
        if not documents:
            documents = [
                {
                    "title": "Jasmin Catering Knowledge Base",
                    "content": "Vollständige Geschäftsinformationen und Preisstruktur...",
                    "relevance_score": 1.0
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
    
    def get_assistant_info(self) -> Dict:
        """Get information about the current assistant"""
        try:
            assistant = self.client.beta.assistants.retrieve(assistant_id=self.assistant_id)
            return {
                "id": assistant.id,
                "name": assistant.name,
                "model": assistant.model,
                "created_at": str(assistant.created_at),
                "instructions_length": len(assistant.instructions) if assistant.instructions else 0,
                "tools": [tool.type for tool in assistant.tools] if assistant.tools else [],
                "metadata": assistant.metadata
            }
        except Exception as e:
            return {"error": str(e)}