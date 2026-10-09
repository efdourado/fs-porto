# 02 · Instalação

## Requisitos

- Python 3.10+ (testado com 3.12)
- Node.js 18+ (testado com 22)
- Uma chave de IA compatível com a API da OpenAI. Recomendado: [OpenRouter](https://openrouter.ai/keys)
- Uma conta no [Pinecone](https://app.pinecone.io) (o plano gratuito *Starter* é suficiente)

## 1. Backend

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

O ambiente virtual (`.venv/`) isola as dependências do projeto do Python do sistema. Todos os comandos usam `.venv/bin/python` e `.venv/bin/uvicorn` para garantir que é esse ambiente que roda.

## 2. Chave de IA

O projeto usa um único cliente de IA (veja [`ai_config.py`](../ai_config.py)) para duas coisas:

| Uso | Variável | Valor padrão no exemplo |
|---|---|---|
| Embeddings (vetores) | `EMBEDDING_MODEL` | `openai/text-embedding-3-small` |
| Chat (respostas do modo pergunta) | `AI_MODEL` | `openrouter/free` |

O chat pode ser gratuito (`openrouter/free` escolhe automaticamente um modelo grátis). O embedding `openai/text-embedding-3-small` é pago, mas custa US$ 0,02 por milhão de tokens: indexar os 12 contratos custa uma fração de centavo. Basta ter um pequeno crédito na conta do OpenRouter.

> Existem modelos de embedding gratuitos no OpenRouter (ex.: `nvidia/nemotron-3-embed-1b:free`), mas os termos dizem que as requisições podem ser usadas para treino. Os contratos têm nomes e CPFs: pense nisso antes de trocar. Se trocar, ajuste `EMBEDDING_DIM` e crie o índice com a dimensão nova.

## 3. Índice no Pinecone

1. Crie a conta em [app.pinecone.io](https://app.pinecone.io) e copie a **API key**.
2. Crie um índice com:
   - **Nome:** `porto`
   - **Dimensão:** `1536` (precisa ser igual a `EMBEDDING_DIM`)
   - **Métrica:** `cosine`
   - **Tipo:** Serverless, AWS, `us-east-1` (a região do plano gratuito)
   - Não use "integrated embedding": este projeto gera os próprios vetores.
3. Abra a página do índice e copie o **Host** (`https://porto-xxxx.svc....pinecone.io`).

O host só existe depois que o índice é criado. Também dá para criar o índice por código:

```python
from pinecone import Pinecone, ServerlessSpec
pc = Pinecone(api_key="pcsk_...")
pc.create_index(name="porto", dimension=1536, metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"))
print(pc.describe_index("porto").host)
```

## 4. Arquivo `.env`

```bash
cp .env.example .env
```

Preencha as chaves. Cada variável está explicada em [`.env.example`](../.env.example). O `.env` está no `.gitignore` e nunca deve ir para o git.

Depois verifique:

```bash
.venv/bin/python check_env.py
```

Saída esperada:

```
[OK]   Embeddings (openai/text-embedding-3-small): dim=1536
[OK]   Chat (openrouter/free): ok
[OK]   Pinecone index: dim=1536, vetores=0

Tudo certo!
```

## 5. Indexar os contratos

```bash
.venv/bin/python processar_contrato.py                     # todos os PDFs de contratos/
.venv/bin/python processar_contrato.py contratos/arquivo.pdf  # só um
```

Rodar de novo é seguro: os IDs dos chunks são fixos (`<nome do arquivo>_<n>`), então o Pinecone sobrescreve em vez de duplicar. Ao final, `check_env.py` deve mostrar `vetores=132`.

## 6. Subir tudo

Um terminal para cada:

```bash
.venv/bin/uvicorn api_pinecone:app --port 8000 --reload
.venv/bin/uvicorn api_upload:app --port 8001 --reload
cd frontend && npm install && npm run dev
```

- Interface: http://localhost:5173
- Documentação interativa da API (gerada pelo FastAPI): http://127.0.0.1:8000/docs e http://127.0.0.1:8001/docs

`--reload` reinicia o servidor sempre que um `.py` muda: ótimo para estudar editando o código.

## Solução de problemas

Problemas reais encontrados ao colocar o projeto para rodar:

| Sintoma | Causa | Solução |
|---|---|---|
| `No matching distribution found for pinecone-client==5.4.2` | O pacote foi renomeado para `pinecone` a partir da 5.1 | Já corrigido no `requirements.txt` (`pinecone==5.4.2`) |
| `401 User not found` (OpenRouter) | Chave incompleta ou inválida | Uma chave válida tem `sk-or-v1-` + 64 caracteres hexadecimais |
| Embedding falha com nome de modelo inválido | No OpenRouter o modelo precisa do prefixo | `EMBEDDING_MODEL=openai/text-embedding-3-small` |
| `sh: vite: Permission denied` | `node_modules` veio de outra máquina sem permissão de execução | Apague `frontend/node_modules` e rode `npm install` |
| "Nenhum contrato disponível" na página Contratos | A listagem consultava o Pinecone com um vetor de zeros | Corrigido: agora usa `index.list()` + `fetch()` |
| `dimensão do índice é X, precisa ser 1536` | Índice criado com dimensão diferente do modelo | Recrie o índice com a dimensão de `EMBEDDING_DIM` |
| `Connection error` com chave vazia | A biblioteca recusa o cabeçalho `Bearer ` sem chave | Preencha `AI_API_KEY` |
