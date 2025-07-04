"""
Azure AI Assistant with Enhanced RAG for Jasmin Catering
Uses Azure OpenAI with embedded knowledge base
"""

import os
import requests
import time
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from config.settings import AI_CONFIG, BUSINESS_CONFIG

class JasminAIAssistantRAG:
    """AI Assistant with enhanced RAG capabilities using embedded knowledge"""
    
    def __init__(self):
        self.ai_endpoint = AI_CONFIG['endpoint']
        self.ai_key = AI_CONFIG['api_key']
        self.knowledge_base = self._load_knowledge_base()
        
    def _load_knowledge_base(self) -> Dict[str, str]:
        """Load all knowledge documents into memory"""
        knowledge_base = {}
        documents_path = Path(__file__).parent.parent / "deployments" / "documents"
        
        knowledge_files = {
            "catering_brief": "catering-brief.md",
            "business_conditions": "business-conditions.md",
            "vegetarian_template": "vegetarian-offer-template.md",
            "response_examples": "response-examples.md",
            "email_template": "email-template.md"
        }
        
        for key, filename in knowledge_files.items():
            file_path = documents_path / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    knowledge_base[key] = f.read()
                print(f"✅ Loaded knowledge: {filename}")
            else:
                print(f"⚠️  Knowledge file not found: {filename}")
                
        return knowledge_base
    
    def _search_knowledge_base(self, query: str, top: int = 3) -> List[Dict]:
        """Search knowledge base for relevant content"""
        # Simple keyword-based search in our knowledge documents
        query_lower = query.lower()
        relevant_docs = []
        
        # Check each document for relevance
        relevance_scores = {}
        for doc_name, content in self.knowledge_base.items():
            content_lower = content.lower()
            
            # Calculate relevance score based on keyword matches
            score = 0
            keywords = query_lower.split()
            for keyword in keywords:
                if len(keyword) > 3:  # Skip short words
                    score += content_lower.count(keyword)
            
            if score > 0:
                relevance_scores[doc_name] = score
        
        # Sort by relevance and get top documents
        sorted_docs = sorted(relevance_scores.items(), key=lambda x: x[1], reverse=True)
        
        for doc_name, score in sorted_docs[:top]:
            content = self.knowledge_base[doc_name]
            # Extract most relevant section (first 1000 chars for now)
            snippet = content[:1000] + "..." if len(content) > 1000 else content
            
            relevant_docs.append({
                "title": doc_name.replace("_", " ").title(),
                "content": snippet,
                "relevance_score": score
            })
        
        # Always include business conditions for pricing
        if "business_conditions" not in [d["title"].lower().replace(" ", "_") for d in relevant_docs]:
            if "business_conditions" in self.knowledge_base:
                relevant_docs.append({
                    "title": "Business Conditions",
                    "content": self.knowledge_base["business_conditions"][:1000] + "...",
                    "relevance_score": 1
                })
        
        return relevant_docs
    
    def generate_response(self, email_subject: str, email_body: str) -> Tuple[str, List[Dict], Dict]:
        """Generate AI response with enhanced RAG context"""
        start_time = time.time()
        
        # Search for relevant documents
        search_query = f"{email_subject} {email_body}"
        documents_used = self._search_knowledge_base(search_query, top=4)
        
        # Build enhanced RAG context
        rag_context = "\n\n".join([
            f"### {doc['title']} (Relevance: {doc['relevance_score']})\n{doc['content']}"
            for doc in documents_used
        ])
        
        # Build comprehensive system prompt
        system_prompt = self._build_enhanced_system_prompt(rag_context)
        
        # Call Azure OpenAI
        headers = {
            'Content-Type': 'application/json',
            'api-key': self.ai_key
        }
        
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Betreff: {email_subject}\n\n{email_body}"}
            ],
            "temperature": AI_CONFIG['temperature'],
            "max_tokens": AI_CONFIG['max_tokens']
        }
        
        try:
            response = requests.post(
                f"{self.ai_endpoint}/openai/deployments/{AI_CONFIG['deployment_name']}/chat/completions?api-version=2024-02-01",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                ai_response = response.json()['choices'][0]['message']['content']
                processing_time = time.time() - start_time
                
                # Extract pricing from response
                pricing_info = self._extract_pricing(ai_response)
                
                return ai_response, documents_used, {
                    'pricing': pricing_info,
                    'processing_time': f"{processing_time:.2f}s",
                    'documents_used': len(documents_used),
                    'rag_type': 'enhanced_embedded'
                }
            else:
                print(f"❌ AI API Error: {response.status_code} - {response.text}")
                return None, [], {}
            
        except Exception as e:
            print(f"❌ AI generation error: {e}")
            return None, [], {}
    
    def _build_enhanced_system_prompt(self, rag_context: str) -> str:
        """Build enhanced system prompt with comprehensive business knowledge"""
        packages = BUSINESS_CONFIG['packages']
        discounts = BUSINESS_CONFIG['discounts']
        surcharges = BUSINESS_CONFIG['surcharges']
        
        # Load full email template if available
        email_template = self.knowledge_base.get('email_template', '')
        
        return f"""Du bist der professionelle Kundenberater von {BUSINESS_CONFIG['name']}, einem renommierten syrischen Fusion-Catering-Service in {BUSINESS_CONFIG['location']}.

VERWENDE DIESE WISSENSDATENBANK FÜR DEINE ANTWORTEN:
{rag_context}

GESCHÄFTSINFORMATIONEN:
- Spezialität: Authentische syrische Küche mit moderner deutscher Fusion
- Liefergebiet: {BUSINESS_CONFIG['service_area']}
- Mindestbestellung: {BUSINESS_CONFIG['min_order']} Personen
- Vorlaufzeit: {BUSINESS_CONFIG['advance_notice']} Stunden minimum
- Qualität: Frische Zutaten, halal-zertifiziert, hausgemachte Spezialitäten

AKTUELLE PREISSTRUKTUR & PAKETE:
**{packages['basis']['name']} ({packages['basis']['price_range'][0]}-{packages['basis']['price_range'][1]}€/Person):** 
- 3-4 authentische Vorspeisen (Hummus, Tabouleh, Fattoush, Baba Ghanoush)
- 2-3 Hauptgerichte (Shish Taouk, Falafel, Kibbeh)
- Basisbeilagen: Reis, Bulgur, frisches Pita-Brot
- Dessert: Baklava oder Ma'amoul

**{packages['standard']['name']} ({packages['standard']['price_range'][0]}-{packages['standard']['price_range'][1]}€/Person):** 
- 5-6 Vorspeisen (Basis + Muhammara, Labneh, gefüllte Weinblätter)
- 3-4 Hauptgerichte (Basis + Lamb Kofta, Sauerbraten Shawarma Fusion)
- Premium-Beilagen: Safran-Reis, Za'atar-Brot, Tabouleh
- Dessert-Auswahl: Baklava, Ma'amoul, Halva

**{packages['premium']['name']} ({packages['premium']['price_range'][0]}-{packages['premium']['price_range'][1]}€/Person):** 
- 8-10 Meze-Vorspeisen (vollständige Auswahl)
- 5-6 Hauptgerichte (alle + Syrian Wagyu, Premium Lamm, Meeresfrüchte)
- Getränke-Service: Arabischer Kaffee, Tee-Service, Ayran
- Vollständiges Dessert-Buffet mit Live-Station
- Professionelles Service-Personal inklusive

RABATTE (kumulierbar bis max. 20%):
- Werktags (Mo-Do): {int(discounts['weekday']*100)}% Rabatt
- Große Gruppen 50+: {int(discounts['large_group']*100)}% Rabatt
- Gemeinnützige Organisationen: {int(discounts['nonprofit']*100)}% Rabatt
- Stammkunden (3+ Buchungen): {int(discounts['loyalty']*100)}% Rabatt

ZUSCHLÄGE:
- Wochenende (Sa-So): +{int(surcharges['weekend']*100)}%
- Eilauftrag (<48h): +{int(surcharges['rush']*100)}%
- Feiertage: +{int(surcharges['holiday']*100)}%
- Hochsaison (Mai-Oktober): +{int(surcharges['summer']*100)}%

EMAIL-VORLAGE STRUKTUR:
{email_template[:500] if email_template else 'Verwende professionelle deutsche Geschäftskorrespondenz'}

WICHTIGE ANWEISUNGEN:
1. ERSTELLE IMMER drei detaillierte, preislich gestaffelte Angebote
2. VERWENDE die Informationen aus der Wissensdatenbank für authentische Details
3. BERECHNE Preise transparent mit allen Rabatten/Zuschlägen
4. PERSONALISIERE die Antwort basierend auf dem Event-Typ
5. SCHLIESSE mit einer Einladung zum persönlichen Beratungsgespräch
6. VERWENDE professionelle, aber herzliche deutsche Geschäftssprache
7. BETONE die Qualität und Einzigartigkeit unserer syrischen Fusion-Küche

NUTZE DIE RAG-DOKUMENTE für spezifische Menü-Details, Geschäftsbedingungen und Email-Formatierung!"""
    
    def _extract_pricing(self, response: str) -> Dict[str, str]:
        """Extract pricing information from AI response"""
        import re
        pricing = {}
        
        patterns = {
            'Basis': r'Basis[^:]*:\s*([0-9.,]+)\s*€',
            'Standard': r'Standard[^:]*:\s*([0-9.,]+)\s*€',
            'Premium': r'Premium[^:]*:\s*([0-9.,]+)\s*€'
        }
        
        for package, pattern in patterns.items():
            matches = re.findall(pattern, response)
            if matches:
                pricing[package] = matches[0] + "€"
        
        return pricing