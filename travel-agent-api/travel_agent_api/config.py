import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

print("*" * 80)
print("[CONFIG] configurazione caricata")
print(f"[CONFIG] modello OpenAI: {OPENAI_MODEL}")
print(f"[CONFIG] OPENAI_API_KEY presente: {bool(OPENAI_API_KEY)}")
print(f"[CONFIG] SERPAPI_API_KEY presente: {bool(SERPAPI_API_KEY)}")
print("*" * 80)