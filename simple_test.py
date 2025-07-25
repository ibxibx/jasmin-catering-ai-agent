import os
from dotenv import load_dotenv

load_dotenv()

print("Environment test:")
print("AZURE_OPENAI_ENDPOINT:", os.getenv('AZURE_OPENAI_ENDPOINT'))
print("AZURE_OPENAI_API_KEY exists:", bool(os.getenv('AZURE_OPENAI_API_KEY')))

try:
    from core.ai_assistant_openai_agent import JasminAIAssistantOpenAI
    print("AI Assistant import: SUCCESS")
    
    ai = JasminAIAssistantOpenAI()
    print("AI Assistant init: SUCCESS")
    print("Assistant ID:", ai.assistant_id)
    
except Exception as e:
    print("AI Assistant error:", str(e))

print("Test completed")
