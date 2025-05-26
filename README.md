# Contratus AI  - Sistema de Consulta de Contratos

Um sistema moderno para processamento e consulta semântica de contratos, utilizando Python, Pinecone e SvelteKit. Permite busca semântica e perguntas em linguagem natural sobre contratos.

## Estrutura do Projeto

```
├── api_pinecone.py       # API principal com FastAPI
├── api_upload.py         # API para upload de contratos
├── llm_router.py         # Roteador para perguntas ao LLM
├── pinecone_utils.py     # Utilitários para Pinecone
├── processar_contrato.py # Processamento de contratos
├── shared.py             # Funções e modelos compartilhados
├── contratos/            # Diretório para armazenar os contratos
├── frontend/             # Aplicação SvelteKit
├── diagrama_modulos.md   # Diagrama das relações entre módulos
└── .env                  # Variáveis de ambiente
```

Para uma visão detalhada de como os módulos do backend se relacionam, consulte o arquivo [diagrama_modulos.md](diagrama_modulos.md).

- **Backend (Python + FastAPI)**
  - `processar_contrato.py`: Processamento automático de PDFs e geração de embeddings
  - `api_pinecone.py`: API REST para busca semântica de contratos usando Pinecone
  - `api_upload.py`: API para upload e processamento automático de novos contratos
  - `pinecone_utils.py`: Biblioteca de utilidades para interação com o Pinecone
  - `llm_router.py`: Roteador para processamento de perguntas com LLM
  - `shared.py`: Funções compartilhadas entre os módulos

- **Frontend (SvelteKit)**
  - Interface moderna e responsiva com Tailwind CSS e DaisyUI
  - Busca semântica em linguagem natural
  - Visualização de contratos
  - Modo de pergunta para consultas em linguagem natural

## Explicação dos Códigos Backend

### 1. `pinecone_utils.py`

**Função**: Biblioteca de utilidades para interação com o Pinecone (banco de dados vetorial).

**Principais funcionalidades**:
- Conexão com o Pinecone
- Geração de embeddings usando OpenAI (modelo text-embedding-3-small)
- Indexação de documentos
- Busca semântica de documentos
- Listagem de documentos no índice

Este arquivo funciona como uma biblioteca de funções auxiliares e não precisa ser executado diretamente.

### 2. `processar_contrato.py`

**Função**: Processamento de contratos em PDF e indexação no Pinecone.

**Principais funcionalidades**:
- Carrega arquivos PDF usando LangChain
- Divide documentos em chunks menores
- Gera embeddings para cada chunk
- Indexa os chunks no Pinecone com metadados
- Pode processar um único contrato ou todos os contratos em uma pasta

Este arquivo pode ser executado diretamente para processar contratos:
- Para processar todos os contratos: `python processar_contrato.py`
- Para processar um contrato específico: `python processar_contrato.py caminho/para/contrato.pdf`

### 3. `api_pinecone.py`

**Função**: API REST para busca semântica de contratos usando FastAPI.

**Principais funcionalidades**:
- Endpoint para listar todos os contratos
- Endpoint para busca semântica por consulta em linguagem natural
- Endpoint para listar arquivos únicos no índice
- Gerenciamento de conexão com Pinecone
- Integração com o roteador LLM para perguntas em linguagem natural

Este arquivo inicia um servidor web na porta 8000 quando executado: `python api_pinecone.py`

### 4. `api_upload.py`

**Função**: API REST para upload e processamento automático de novos contratos.

**Principais funcionalidades**:
- Endpoint para upload de arquivos PDF
- Processamento assíncrono dos contratos enviados
- Endpoint para listar contratos disponíveis na pasta

Este arquivo inicia um servidor web na porta 8001 quando executado: `python api_upload.py`

### 5. `llm_router.py`

**Função**: Roteador para processamento de perguntas usando LLM (Large Language Model).

**Principais funcionalidades**:
- Endpoint para responder perguntas sobre contratos usando o LLM
- Integração com a busca semântica para fornecer contexto ao LLM
- Formatação de respostas com citação de fontes

Este arquivo é importado pelo `api_pinecone.py` e não precisa ser executado diretamente.

### 6. `shared.py`

**Função**: Funções e modelos compartilhados entre os diferentes módulos.

**Principais funcionalidades**:
- Função compartilhada para busca de contratos
- Modelos de dados para respostas da API

Este arquivo é importado por outros módulos e não precisa ser executado diretamente.

## Requisitos

- Python 3.8+
- Node.js 18+
- Conta no Pinecone (https://www.pinecone.io/)
- Chave de API da OpenAI (https://platform.openai.com/)

## Configuração

1. **Backend**

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente (.env)
OPENAI_API_KEY=sua_chave_api_openai
PINECONE_API_KEY=sua_chave_api_pinecone
PINECONE_HOST=seu_host_pinecone
PINECONE_INDEX_NAME=brito-ai
OPENAI_MODEL=gpt-4o-mini  # Opcional, padrão é gpt-4o-mini

# Processar contratos existentes
python processar_contrato.py

# Processar apenas um contrato específico
python processar_contrato.py contratos\EDUARD ROCHA FONTENELE.pdf

# Iniciar a API de busca semântica com Uvicorn
uvicorn api_pinecone:app --host 127.0.0.1 --port 8000 --reload

# Iniciar a API de upload (em outra janela do terminal)
uvicorn api_upload:app --host 127.0.0.1 --port 8001 --reload
```

**Nota importante:** O índice vetorial no Pinecone (`brito-ai`) deve ser criado manualmente através do painel de controle do Pinecone, usando o modelo `text-embedding-3-small` da OpenAI com dimensão 1536.

2. **Frontend**

```bash
# Entrar no diretório do frontend
cd frontend

# Instalar dependências
npm install

# Iniciar em modo desenvolvimento
npm run dev
```

## Ordem de Execução Recomendada

1. **Processamento inicial de contratos** (se necessário):
   ```
   python processar_contrato.py
   ```
   Este passo é opcional se os contratos já foram processados e indexados no Pinecone.

2. **Iniciar a API de busca semântica**:
   ```
   uvicorn api_pinecone:app --host 127.0.0.1 --port 8000 --reload
   ```
   Esta API é essencial para o funcionamento do frontend, pois fornece a capacidade de busca semântica e o modo de pergunta com LLM.

3. **Iniciar a API de upload** (opcional, se quiser permitir upload de novos contratos):
   ```
   uvicorn api_upload:app --host 127.0.0.1 --port 8001 --reload
   ```
   Este passo é opcional se não houver necessidade de fazer upload de novos contratos.

4. **Iniciar o frontend**:
   ```
   cd frontend
   npm install (se ainda não tiver instalado as dependências)
   npm run dev
   ```
   Isso iniciará o servidor de desenvolvimento do SvelteKit na porta 5173.

Após esses passos, você poderá acessar a aplicação em `http://localhost:5173` e realizar consultas semânticas aos contratos já indexados no Pinecone.

## Uso

### Processamento de Contratos

1. Coloque os arquivos PDF dos contratos na pasta `contratos/`
2. Execute `python processar_contrato.py` para processar todos os contratos da pasta
3. Alternativamente, processe um contrato específico: `python processar_contrato.py caminho/para/contrato.pdf`

### Upload de Novos Contratos

1. Inicie a API de upload: `uvicorn api_upload:app --host 127.0.0.1 --port 8001 --reload`
2. Envie novos contratos via endpoint POST `/upload/contrato`
3. Os contratos enviados serão processados automaticamente em segundo plano

### Consulta de Contratos

1. Acesse o frontend em `http://localhost:5173`
2. Use a barra de busca para consultar contratos em linguagem natural
3. Visualize os resultados ordenados por relevância
4. Alternativamente, use a API diretamente via endpoint GET `/contratos/busca?q=sua consulta`

### Modo Pergunta (LLM)

1. Acesse o frontend em `http://localhost:5173`
2. Ative o switch "Modo Pergunta" ao lado da barra de busca
3. Digite sua pergunta em linguagem natural (ex: "Qual o valor do aluguel que Eduardo paga?" ou "Temos informações de boleto?")
4. Clique em "Buscar" para obter uma resposta detalhada baseada nos contratos relevantes

Alternativamente, use a API diretamente via endpoint POST `/llm/ask` com um JSON no formato:
```json
{
  "question": "Sua pergunta aqui",
  "max_results": 3
}
```

O sistema utiliza o modelo configurado na variável de ambiente `OPENAI_MODEL` (padrão: gpt-4o-mini) para gerar respostas detalhadas com base nos contratos encontrados na busca semântica.

## Tecnologias

- **Backend**:
  - Python
  - FastAPI
  - Uvicorn (servidor ASGI)
  - Pinecone (banco de dados vetorial)
  - OpenAI Embeddings (modelo text-embedding-3-small)
  - OpenAI Chat Completions (modelo gpt-4o-mini padrão)
  - LangChain (processamento de documentos)
  
- **Frontend**:
  - SvelteKit
  - Tailwind CSS
  - DaisyUI

## Documentação das APIs

### API de Busca Semântica (api_pinecone.py)

**Porta**: 8000

| Endpoint | Método | Descrição | Parâmetros |
|----------|--------|-----------|------------|
| `/` | GET | Verifica o status da API e a conexão com o Pinecone | - |
| `/contratos/lista` | GET | Lista todos os contratos disponíveis | `skip`: número de registros para pular<br>`limit`: número máximo de registros para retornar |
| `/contratos/busca` | GET | Realiza uma busca semântica nos contratos | `q`: consulta para busca<br>`limit`: número máximo de resultados |
| `/contratos/arquivos` | GET | Lista todos os nomes de arquivos únicos no índice | - |
| `/llm/ask` | POST | Responde a perguntas sobre contratos usando o LLM | Body JSON: `{"question": "string", "max_results": int}` |

### API de Upload (api_upload.py)

**Porta**: 8001

| Endpoint | Método | Descrição | Parâmetros |
|----------|--------|-----------|------------|
| `/upload/contrato` | POST | Faz upload de um novo contrato PDF e o processa automaticamente | Form Data: `file`: arquivo PDF |
| `/contratos/lista` | GET | Lista todos os contratos disponíveis na pasta de contratos | - |

## Inicialização com Uvicorn

O Uvicorn é um servidor ASGI (Asynchronous Server Gateway Interface) de alto desempenho que é recomendado para aplicações FastAPI. Para iniciar as APIs com Uvicorn, siga os comandos abaixo:

### API de Busca Semântica

```bash
uvicorn api_pinecone:app --host 127.0.0.1 --port 8000 --reload
```

Opções importantes:
- `--host 127.0.0.1`: Limita o acesso apenas ao localhost
- `--port 8000`: Define a porta 8000 para a API
- `--reload`: Ativa o modo de recarga automática (útil para desenvolvimento)

### API de Upload

```bash
uvicorn api_upload:app --host 127.0.0.1 --port 8001 --reload
```

Para produção, remova a flag `--reload` e considere usar `--host 0.0.0.0` se precisar acessar a API de outros dispositivos na rede.

## Atualizações Recentes

- **Correção do modo pergunta (LLM)**: Resolvido o problema que afetava o modo pergunta após o processamento de novos contratos. A solução envolveu modificar o `llm_router.py` para acessar diretamente a função `buscar_documentos` do módulo `pinecone_utils.py`, contornando a incompatibilidade de formato com a função `buscar_contratos`.

- **Melhoria no tratamento de erros**: Implementado tratamento de erros mais robusto em toda a aplicação, com mensagens mais claras e logs detalhados para facilitar a depuração.

- **Otimização do frontend**: Melhorado o tratamento de erros no frontend para exibir mensagens mais claras ao usuário.

- **Processamento de novos contratos**: Adicionados e processados novos contratos (contrato_joao_silva.pdf e contrato_maria_oliveira.pdf).

- **Atualização da documentação**: Melhorada a documentação com instruções detalhadas para inicialização e uso do sistema.
