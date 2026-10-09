"""Verifica se as chaves do .env funcionam: python check_env.py"""
import os
from pinecone import Pinecone
from ai_config import ai_client, AI_BASE_URL, AI_API_KEY, AI_MODEL, EMBEDDING_MODEL, EMBEDDING_DIM

ok = True

def check(nome, fn):
    global ok
    try:
        print(f"[OK]   {nome}: {fn()}")
    except Exception as e:
        ok = False
        print(f"[FAIL] {nome}: {e}")

print(f"Provedor: {AI_BASE_URL or 'OpenAI (padrão)'}\n")
for var, val in [("AI_API_KEY", AI_API_KEY)] + [(v, os.getenv(v)) for v in ["PINECONE_API_KEY", "PINECONE_HOST", "PINECONE_INDEX_NAME"]]:
    if not val:
        ok = False
        print(f"[FAIL] {var} vazio no .env")

def embedding_check():
    dim = len(ai_client.embeddings.create(input="teste de contrato", model=EMBEDDING_MODEL).data[0].embedding)
    if dim != EMBEDDING_DIM:
        raise ValueError(f"modelo retornou dim={dim}, mas EMBEDDING_DIM={EMBEDDING_DIM}")
    return f"dim={dim}"

check(f"Embeddings ({EMBEDDING_MODEL})", embedding_check)
check(f"Chat ({AI_MODEL})",
      lambda: ai_client.chat.completions.create(model=AI_MODEL, messages=[{"role": "user", "content": "Responda só: ok"}]).choices[0].message.content)

def pinecone_check():
    index = Pinecone(api_key=os.getenv("PINECONE_API_KEY")).Index(os.getenv("PINECONE_INDEX_NAME"), host=os.getenv("PINECONE_HOST"))
    stats = index.describe_index_stats()
    dim = stats.get("dimension")
    if dim != EMBEDDING_DIM:
        raise ValueError(f"dimensão do índice é {dim}, precisa ser {EMBEDDING_DIM}")
    return f"dim={dim}, vetores={stats.get('total_vector_count', 0)}"

check("Pinecone index", pinecone_check)
print("\nTudo certo!" if ok else "\nCorrija os itens [FAIL] acima.")
