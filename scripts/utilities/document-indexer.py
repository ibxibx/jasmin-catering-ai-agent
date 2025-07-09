#!/usr/bin/env python3
"""
Azure AI Search Document Indexer for Jasmin Catering RAG System
Uploads and indexes business knowledge documents for enhanced AI responses
"""

import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any
import requests
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    VectorSearchProfile,
    VectorSearchAlgorithmConfiguration,
    HnswAlgorithmConfiguration
)
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

class JasminCateringIndexer:
    def __init__(self):
        self.search_service_name = "jasmin-catering-search"
        self.index_name = "jasmin-catering-knowledge"
        self.search_endpoint = f"https://{self.search_service_name}.search.windows.net"
        
        # Get credentials from environment
        self.search_api_key = os.getenv('AZURE_SEARCH_API_KEY')
        self.openai_api_key = os.getenv('AZURE_AI_API_KEY')
        self.openai_endpoint = "https://swedencentral.api.cognitive.microsoft.com"
        
        if not self.search_api_key:
            print("⚠️  AZURE_SEARCH_API_KEY not found in environment")
            print("   Get it with: az search admin-key show --service-name jasmin-catering-search --resource-group logicapp-jasmin-sweden_group")
        
        if not self.openai_api_key:
            print("⚠️  AZURE_AI_API_KEY not found in environment")
    
    def get_search_api_key(self):
        """Get Azure Search API key via CLI"""
        try:
            import subprocess
            result = subprocess.run([
                'az', 'search', 'admin-key', 'show',
                '--service-name', self.search_service_name,
                '--resource-group', 'logicapp-jasmin-sweden_group',
                '--query', 'primaryKey',
                '-o', 'tsv'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"❌ Failed to get search API key: {result.stderr}")
                return None
        except Exception as e:
            print(f"❌ Error getting search API key: {e}")
            return None
    
    def generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings using Azure OpenAI"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'api-key': self.openai_api_key
            }
            
            payload = {
                'input': text,
                'model': 'text-embedding-ada-002'
            }
            
            response = requests.post(
                f"{self.openai_endpoint}/openai/deployments/text-embedding-ada-002/embeddings?api-version=2023-05-15",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()['data'][0]['embedding']
            else:
                print(f"❌ Embedding generation failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error generating embeddings: {e}")
            return None
    
    def create_search_index(self):
        """Create the search index with vector search capabilities"""
        
        if not self.search_api_key:
            self.search_api_key = self.get_search_api_key()
            if not self.search_api_key:
                return False
        
        try:
            credential = AzureKeyCredential(self.search_api_key)
            index_client = SearchIndexClient(
                endpoint=self.search_endpoint,
                credential=credential
            )
            
            # Define the search index schema
            fields = [
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                SearchableField(name="title", type=SearchFieldDataType.String),
                SearchableField(name="content", type=SearchFieldDataType.String),
                SearchableField(name="category", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="file_path", type=SearchFieldDataType.String),
                SimpleField(name="last_modified", type=SearchFieldDataType.DateTimeOffset),
                SearchField(
                    name="content_vector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=1536,
                    vector_search_profile_name="default-vector-profile"
                )
            ]
            
            # Configure vector search
            vector_search = VectorSearch(
                profiles=[
                    VectorSearchProfile(
                        name="default-vector-profile",
                        algorithm_configuration_name="default-algorithm"
                    )
                ],
                algorithms=[
                    HnswAlgorithmConfiguration(
                        name="default-algorithm"
                    )
                ]
            )
            
            # Create the search index
            index = SearchIndex(
                name=self.index_name,
                fields=fields,
                vector_search=vector_search
            )
            
            result = index_client.create_or_update_index(index)
            print(f"✅ Search index '{self.index_name}' created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error creating search index: {e}")
            return False
    
    def process_markdown_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a markdown file and extract content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title from first header
            lines = content.split('\n')
            title = file_path.stem.replace('-', ' ').title()
            for line in lines:
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
            
            # Determine category based on filename
            filename = file_path.stem
            if 'business' in filename or 'info' in filename:
                category = 'business-info'
            elif 'menu' in filename or 'offering' in filename:
                category = 'menu-offerings'
            elif 'pricing' in filename or 'price' in filename:
                category = 'pricing'
            elif 'policy' in filename or 'service' in filename:
                category = 'policies'
            else:
                category = 'general'
            
            # Generate document ID
            doc_id = hashlib.md5(str(file_path).encode()).hexdigest()
            
            from datetime import datetime
            
            return {
                'id': doc_id,
                'title': title,
                'content': content,
                'category': category,
                'file_path': str(file_path),
                'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat() + 'Z'
            }
            
        except Exception as e:
            print(f"❌ Error processing file {file_path}: {e}")
            return None
    
    def upload_documents(self, documents_dir: str = "knowledge-base/documents"):
        """Upload all documents from the knowledge base directory"""
        
        if not self.search_api_key:
            self.search_api_key = self.get_search_api_key()
            if not self.search_api_key:
                return False
        
        try:
            credential = AzureKeyCredential(self.search_api_key)
            search_client = SearchClient(
                endpoint=self.search_endpoint,
                index_name=self.index_name,
                credential=credential
            )
            
            documents_path = Path(documents_dir)
            if not documents_path.exists():
                print(f"❌ Documents directory not found: {documents_path}")
                return False
            
            documents = []
            markdown_files = list(documents_path.glob("*.md"))
            
            if not markdown_files:
                print(f"❌ No markdown files found in {documents_path}")
                return False
            
            print(f"📚 Processing {len(markdown_files)} documents...")
            
            for file_path in markdown_files:
                print(f"   📄 Processing: {file_path.name}")
                
                doc_data = self.process_markdown_file(file_path)
                if not doc_data:
                    continue
                
                # Generate embeddings for the content
                print(f"   🔍 Generating embeddings...")
                embeddings = self.generate_embeddings(doc_data['content'])
                if embeddings:
                    doc_data['content_vector'] = embeddings
                    documents.append(doc_data)
                    print(f"   ✅ Processed: {doc_data['title']}")
                else:
                    print(f"   ⚠️  Skipping {file_path.name} - embedding generation failed")
            
            if documents:
                print(f"\n📤 Uploading {len(documents)} documents to search index...")
                result = search_client.upload_documents(documents)
                
                success_count = sum(1 for r in result if r.succeeded)
                failed_count = len(result) - success_count
                
                print(f"✅ Upload complete: {success_count} successful, {failed_count} failed")
                
                if failed_count > 0:
                    for r in result:
                        if not r.succeeded:
                            print(f"   ❌ Failed: {r.key} - {r.error_message}")
                
                return success_count > 0
            else:
                print("❌ No documents were processed successfully")
                return False
                
        except Exception as e:
            print(f"❌ Error uploading documents: {e}")
            return False
    
    def test_search(self, query: str = "Syrian menu options"):
        """Test the search functionality"""
        
        if not self.search_api_key:
            self.search_api_key = self.get_search_api_key()
            if not self.search_api_key:
                return False
        
        try:
            credential = AzureKeyCredential(self.search_api_key)
            search_client = SearchClient(
                endpoint=self.search_endpoint,
                index_name=self.index_name,
                credential=credential
            )
            
            print(f"🔍 Testing search with query: '{query}'")
            
            results = search_client.search(
                search_text=query,
                top=3,
                include_total_count=True
            )
            
            print(f"📊 Found {results.get_count()} total results")
            
            for i, result in enumerate(results, 1):
                print(f"\n📄 Result {i}:")
                print(f"   Title: {result['title']}")
                print(f"   Category: {result['category']}")
                print(f"   Score: {result['@search.score']:.4f}")
                print(f"   Content Preview: {result['content'][:200]}...")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing search: {e}")
            return False

def main():
    print("🚀 Jasmin Catering RAG System - Document Indexer")
    print("=" * 55)
    
    indexer = JasminCateringIndexer()
    
    # Step 1: Create search index
    print("\n📋 Step 1: Creating search index...")
    if not indexer.create_search_index():
        print("❌ Failed to create search index. Exiting.")
        return
    
    # Step 2: Upload documents
    print("\n📚 Step 2: Uploading knowledge base documents...")
    if not indexer.upload_documents():
        print("❌ Failed to upload documents. Exiting.")
        return
    
    # Step 3: Test search functionality
    print("\n🔍 Step 3: Testing search functionality...")
    indexer.test_search("Syrian appetizers and meze")
    indexer.test_search("pricing for wedding catering")
    indexer.test_search("vegetarian menu options")
    
    print("\n🎉 RAG system setup complete!")
    print("\n💡 Next steps:")
    print("   1. Update AI prompts to use RAG capabilities")
    print("   2. Integrate search into email processing workflow")
    print("   3. Test enhanced AI responses with knowledge base")

if __name__ == "__main__":
    main()