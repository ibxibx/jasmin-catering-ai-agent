# How to Create a Real Azure AI Agent

## Current Situation
- **No AI Agent exists** in your Azure AI Foundry
- Your current resource doesn't support AI Agents/Assistants
- The code uses enhanced local RAG instead

## To Create a Real AI Agent in Azure

### Option 1: Create via Azure AI Foundry Portal (Recommended)

1. **Go to Azure AI Foundry**
   ```
   https://ai.azure.com
   ```

2. **Navigate to your project**
   - Select "jasmin-catering" project
   - Go to "Build" → "Agents"

3. **Create New Agent**
   - Click "Create agent"
   - Name: "Jasmin Catering Agent"
   - Model: "gpt-4o"
   - Enable "File Search" tool

4. **Upload Knowledge Files**
   - Create a vector store
   - Upload these files from `deployments/documents/`:
     - catering-brief.md
     - business-conditions.md
     - vegetarian-offer-template.md
     - response-examples.md
     - email-template.md

5. **Configure Agent Instructions**
   - Copy content from `deployments/documents/jasmin_catering_prompt.md`
   - Paste as agent instructions

### Option 2: Enable Assistants API on Your Resource

1. **Check if Available**
   ```bash
   az cognitiveservices account show \
     --name jasmin-catering-resource \
     --resource-group logicapp-jasmin-sweden_group \
     --query "properties.capabilities[?name=='OpenAI.Assistants']"
   ```

2. **If Not Available**
   - You may need to create a new Azure OpenAI resource
   - Or request Assistants API access for your region

### Option 3: Use Azure OpenAI Studio

1. **Access Azure OpenAI Studio**
   ```
   https://oai.azure.com
   ```

2. **Select your resource**
   - jasmin-catering-resource

3. **Go to Assistants (if available)**
   - Create new assistant
   - Upload files
   - Configure instructions

## Current Workaround

Since AI Agents aren't available, the code uses:
```python
# core/ai_assistant_rag.py
class JasminAIAssistantRAG:
    """Simulates AI Agent behavior with embedded knowledge"""
    
    def __init__(self):
        # Loads knowledge files locally
        self.knowledge_base = self._load_knowledge_base()
    
    def generate_response(self, subject, body):
        # Uses Chat Completions API with RAG context
        # NOT a real AI Agent
```

## To Verify Agent Existence

### Check in Portal:
1. Go to https://ai.azure.com
2. Select jasmin-catering project
3. Navigate to Build → Agents
4. You should see NO agents listed

### Check via CLI:
```bash
# This will likely fail or return empty
az rest --method get \
  --uri "https://jasmin-catering-resource.cognitiveservices.azure.com/openai/assistants?api-version=2024-02-01" \
  --headers "api-key=$AZURE_AI_API_KEY"
```

## Why the Current Solution Works

Even without a real AI Agent:
- ✅ Uses same GPT-4o model
- ✅ Includes all knowledge documents
- ✅ Provides RAG functionality
- ✅ Costs less (no Assistants API fees)
- ✅ Works with your existing setup

## Next Steps

1. **Keep Current Solution**
   - Works well
   - No additional costs
   - Full control

2. **Or Create Real Agent**
   - Use Azure AI Foundry portal
   - Follow steps above
   - Update code to use agent_id

The enhanced RAG implementation provides the same functionality without requiring AI Agents to be available on your Azure resource.