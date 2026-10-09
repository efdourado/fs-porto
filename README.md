# Porto

Sistema de consulta de contratos imobiliários com IA. Você faz uma busca ou uma pergunta em linguagem natural ("qual o valor do aluguel do Bruno?") e o sistema encontra os trechos relevantes dos contratos em PDF e, no modo pergunta, gera uma resposta com um LLM.

É um exemplo completo e pequeno de **RAG** (*Retrieval-Augmented Generation*): PDFs → chunks → embeddings → banco vetorial → busca → resposta do LLM.

| Camada | Tecnologia |
|---|---|
| Backend | Python, FastAPI, LangChain (leitura e divisão dos PDFs) |
| IA | Qualquer API compatível com OpenAI (padrão: OpenRouter) para embeddings e chat |
| Banco vetorial | Pinecone (serverless, plano gratuito) |
| Frontend | SvelteKit, Tailwind CSS |

## Início rápido

Requisitos: Python 3.10+, Node.js 18+, uma chave de IA (OpenRouter ou OpenAI) e uma conta Pinecone.

```bash
# 1. Backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env          # preencha as chaves
.venv/bin/python check_env.py # verifica chaves, modelo e índice

# 2. Indexar os contratos da pasta contratos/ no Pinecone
.venv/bin/python processar_contrato.py

# 3. Subir os serviços (um terminal para cada)
.venv/bin/uvicorn api_pinecone:app --port 8000 --reload   # busca + perguntas
.venv/bin/uvicorn api_upload:app --port 8001 --reload     # upload de PDFs
cd frontend && npm install && npm run dev                  # http://localhost:5173
```

O passo a passo completo (incluindo como criar o índice no Pinecone) está em [docs/02-instalacao.md](docs/02-instalacao.md).

## Documentação

| Documento | Conteúdo |
|---|---|
| [01 · Visão geral](docs/01-visao-geral.md) | Conceitos (RAG, embeddings, chunks, similaridade) e arquitetura |
| [02 · Instalação](docs/02-instalacao.md) | Configuração do zero, variáveis de ambiente, solução de problemas |
| [03 · Backend](docs/03-backend.md) | Cada arquivo Python, função por função |
| [04 · Frontend](docs/04-frontend.md) | Cada arquivo do SvelteKit |
| [05 · API](docs/05-api.md) | Referência dos endpoints com exemplos reais |
| [06 · Roteiro de estudo](docs/06-roteiro-de-estudo.md) | Ordem de leitura, exercícios e problemas conhecidos |

Exemplos prontos de requisições e respostas reais estão em [exemplos/](exemplos/).

## Estrutura

```
├── ai_config.py           # cliente de IA compartilhado (lê o .env)
├── api_pinecone.py        # API de busca e perguntas (porta 8000)
├── api_upload.py          # API de upload de PDFs (porta 8001)
├── llm_router.py          # endpoint /llm/ask (RAG)
├── pinecone_utils.py      # busca semântica usada pelo /llm/ask
├── processar_contrato.py  # PDF → chunks → embeddings → Pinecone
├── shared.py              # modelos e função de busca compartilhados
├── check_env.py           # diagnóstico do .env
├── .env.example           # modelo do .env
├── contratos/             # PDFs de exemplo (12 contratos fictícios)
├── exemplos/              # requisições e respostas de exemplo
├── docs/                  # documentação
└── frontend/              # aplicação SvelteKit
```
