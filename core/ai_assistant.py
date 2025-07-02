"""
Azure AI Assistant with RAG for Jasmin Catering
"""

import requests
import time
from typing import Dict, List, Tuple, Optional
from config.settings import AI_CONFIG, SEARCH_CONFIG, BUSINESS_CONFIG


class JasminAIAssistant:
    """AI Assistant with integrated RAG capabilities"""
    
    def __init__(self):
        self.ai_endpoint = AI_CONFIG['endpoint']
        self.ai_key = AI_CONFIG['api_key']
        self.search_endpoint = SEARCH_CONFIG['endpoint']
        self.search_key = SEARCH_CONFIG['api_key']
        self.index_name = SEARCH_CONFIG['index_name']
        
    def search_knowledge_base(self, query: str, top: int = 3) -> List[Dict]:
        """Search RAG documents in Azure AI Search"""
        headers = {
            'Content-Type': 'application/json',
            'api-key': self.search_key
        }
        
        payload = {
            "search": query,
            "searchMode": "all",
            "top": top,
            "select": "title,content,category"
        }
        
        try:
            response = requests.post(
                f"{self.search_endpoint}/indexes/{self.index_name}/docs/search?api-version=2021-04-30-Preview",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return response.json().get('value', [])
            return []
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def generate_response(self, email_subject: str, email_body: str) -> Tuple[str, List[Dict], Dict]:
        """Generate AI response with RAG context"""
        start_time = time.time()
        
        # Search for relevant documents
        search_queries = [
            email_subject,
            f"{email_subject} pricing packages",
            "catering pricing structure discounts"
        ]
        
        all_docs = []
        for query in search_queries:
            docs = self.search_knowledge_base(query)
            all_docs.extend(docs)
        
        # Remove duplicates and limit to top 4
        unique_docs = {doc['title']: doc for doc in all_docs}.values()
        documents_used = list(unique_docs)[:4]
        
        # Build RAG context
        rag_context = "\n\n".join([
            f"### {doc['title']}\n{doc['content']}"
            for doc in documents_used
        ])
        
        # Build system prompt with embedded business knowledge
        system_prompt = self._build_system_prompt(rag_context)
        
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
                    'documents_used': len(documents_used)
                }
            
            return None, [], {}
            
        except Exception as e:
            print(f"AI generation error: {e}")
            return None, [], {}
    
    def _build_system_prompt(self, rag_context: str) -> str:
        """Build comprehensive system prompt"""
        packages = BUSINESS_CONFIG['packages']
        discounts = BUSINESS_CONFIG['discounts']
        surcharges = BUSINESS_CONFIG['surcharges']
        
        return f"""Du bist der Kundenberater von {BUSINESS_CONFIG['name']}, einem syrischen Fusion-Catering-Service in {BUSINESS_CONFIG['location']}.

WICHTIGE GESCHÄFTSINFORMATIONEN:
- Spezialität: Syrisch-deutsche Fusion-Küche
- Liefergebiet: {BUSINESS_CONFIG['service_area']}
- Mindestbestellung: {BUSINESS_CONFIG['min_order']} Personen
- Vorlaufzeit: {BUSINESS_CONFIG['advance_notice']} Stunden minimum

PREISSTRUKTUR & PAKETE:
**{packages['basis']['name']} ({packages['basis']['price_range'][0]}-{packages['basis']['price_range'][1]}€/Person):** 
- 3-4 Vorspeisen (Hummus, Tabouleh, Fattoush)
- 2-3 Hauptgerichte (Shish Taouk, Falafel)
- Basisbeilagen, Brot

**{packages['standard']['name']} ({packages['standard']['price_range'][0]}-{packages['standard']['price_range'][1]}€/Person):** 
- 4-5 Vorspeisen (+ Baba Ghanoush, Kibbeh)
- 3-4 Hauptgerichte (+ Lamb Kofta, Sauerbraten Shawarma)
- Premium-Beilagen, Dessert-Auswahl

**{packages['premium']['name']} ({packages['premium']['price_range'][0]}-{packages['premium']['price_range'][1]}€/Person):** 
- 6-8 Meze-Vorspeisen
- 4-5 Hauptgerichte (+ Premium Lamm, Syrian Wagyu)
- Vollständiges Dessert-Buffet
- Getränke-Koordination

RABATTE:
- Werktags (Mo-Do): {int(discounts['weekday']*100)}% Rabatt
- Große Gruppen 50+: {int(discounts['large_group']*100)}% Rabatt
- Gemeinnützige Organisationen: {int(discounts['nonprofit']*100)}% Rabatt

ZUSCHLÄGE:
- Wochenende: +{int(surcharges['weekend']*100)}%
- Eilauftrag (<48h): +{int(surcharges['rush']*100)}%

ZUSÄTZLICHE INFORMATIONEN AUS WISSENSDATENBANK:
{rag_context}

AUFGABEN:
1. Erstelle IMMER drei detaillierte Angebotsoptionen (Basis, Standard, Premium)
2. Berechne Preise basierend auf Gruppengröße und zutreffenden Rabatten/Zuschlägen
3. Zeige die Berechnung transparent (Grundpreis × Personen ± Rabatte/Zuschläge)
4. Schlage spezifische Menüs vor
5. Lade zu persönlichem Beratungsgespräch ein"""
    
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
            match = re.search(pattern, response)
            if match:
                pricing[package] = match.group(1) + "€"
        
        return pricing