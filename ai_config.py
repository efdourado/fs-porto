import os
from openai import OpenAI
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env no diretório deste módulo
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

# Provedor compatível com a API da OpenAI (ex.: OpenRouter). Sem AI_BASE_URL, usa a OpenAI direto.
AI_BASE_URL = os.getenv("AI_BASE_URL") or None
AI_API_KEY = os.getenv("AI_API_KEY") or os.getenv("OPENAI_API_KEY")
AI_MODEL = os.getenv("AI_MODEL") or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# O índice do Pinecone precisa ter a mesma dimensão do modelo de embedding
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1536"))

ai_client = OpenAI(api_key=AI_API_KEY, base_url=AI_BASE_URL)
