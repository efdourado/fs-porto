# 06 · Roteiro de estudo

Uma ordem para ler o projeto arquivo por arquivo, com um exercício prático em cada etapa e a lista de problemas conhecidos para corrigir depois.

A regra de ouro: **leia, rode, quebre**. Para cada arquivo, leia a seção correspondente em [03 · Backend](03-backend.md) ou [04 · Frontend](04-frontend.md), abra o código ao lado e faça o exercício. Os servidores com `--reload` reiniciam sozinhos quando você salva.

## Etapa 1 · Configuração

**Ler:** [`.env.example`](../.env.example), [`ai_config.py`](../ai_config.py), [`check_env.py`](../check_env.py)

**Entender:** de onde vêm as chaves, por que a mesma biblioteca `openai` fala com o OpenRouter, o que é a dimensão do embedding.

**Exercício:** abra um terminal Python e gere um embedding na mão:

```python
from ai_config import ai_client, EMBEDDING_MODEL
v = ai_client.embeddings.create(input="multa por rescisão", model=EMBEDDING_MODEL).data[0].embedding
len(v), v[:5]
```

Gere também para "penalidade por quebra de contrato" e para "receita de bolo", e calcule a similaridade de cosseno entre eles (`numpy.dot(a, b) / (norm(a) * norm(b))`). Os dois primeiros devem dar bem mais próximos.

## Etapa 2 · Indexação

**Ler:** [`processar_contrato.py`](../processar_contrato.py)

**Entender:** PDF → páginas → chunks → embeddings → upsert; o formato do ID; os metadados.

**Exercícios:**

1. No console do Pinecone, abra o índice `porto` e procure o ID `Contrato_Altos_Padroes_Construcoes_GR340_X_Bruno_Mendes_Oliveira_3`. Veja os metadados.
2. Repare que esse chunk fala do **valor do aluguel**, mas está com `secao: "Identificação do Locador"`. Por quê? (Dica: ordem dos `if` em `identificar_secao`, e quantas vezes a palavra "locador" aparece num contrato.)
3. Rode o splitter isolado e imprima os chunks de um contrato para ver onde ele corta.

## Etapa 3 · A API principal

**Ler:** [`api_pinecone.py`](../api_pinecone.py)

**Entender:** como o FastAPI declara rotas (`@app.get`), parâmetros (`Query`), modelos de resposta (`response_model`); o `include_router`; o CORS.

**Exercícios:**

1. Abra http://127.0.0.1:8000/docs e execute cada rota pelo Swagger.
2. Faça a mesma busca com `limit=3` e `limit=20` e observe os scores: como eles caem?
3. Leia a seção "Bug do vetor de zeros" abaixo e explique com suas palavras por que a listagem voltava vazia.

## Etapa 4 · RAG

**Ler:** [`pinecone_utils.py`](../pinecone_utils.py) (só `buscar_documentos`) e [`llm_router.py`](../llm_router.py)

**Entender:** recuperação + geração; o prompt de sistema; o "enriquecimento" da consulta.

**Exercícios:**

1. Pergunte *"Qual o valor do aluguel da Ana Carolina Silva?"*. O LLM diz que ela não está nos contratos. Ponha um `print` com os arquivos retornados por `buscar_documentos` e confirme que o contrato dela não veio.
2. Comente o bloco de enriquecimento e pergunte de novo. Melhorou?
3. Mude `temperature` para 0 e para 1.2 e compare as respostas.
4. Mude o prompt de sistema para "responda em uma frase" e veja o efeito.

## Etapa 5 · Código periférico

**Ler:** [`shared.py`](../shared.py), [`api_upload.py`](../api_upload.py)

**Exercício:** faça upload de um PDF pelo [`exemplos/requisicoes.http`](../exemplos/requisicoes.http) e acompanhe o terminal da porta 8001 processando em segundo plano. Depois confirme o novo total em `GET :8000/`.

## Etapa 6 · Frontend

**Ler, nesta ordem:** [`app.css`](../frontend/src/app.css) e [`tailwind.config.js`](../frontend/tailwind.config.js) → [`api.ts`](../frontend/src/lib/services/api.ts) → [`+page.svelte`](../frontend/src/routes/+page.svelte) → [`SearchField.svelte`](../frontend/src/lib/components/SearchField.svelte) → [`contratos.ts`](../frontend/src/lib/contratos.ts) → [`contratos/+page.svelte`](../frontend/src/routes/contratos/+page.svelte) → [`[arquivo]/+page.svelte`](../frontend/src/routes/contratos/[arquivo]/+page.svelte) → [`+layout.svelte`](../frontend/src/routes/+layout.svelte)

**Exercícios:**

1. Abra o DevTools do navegador (aba Network) e veja as chamadas para :8000 enquanto usa a página.
2. Troque `--accent` em `app.css` (ex.: `52 199 89`, o verde da Apple) e veja todos os botões e links mudarem, nos dois temas.
3. Ative o modo escuro do sistema e recarregue: nenhuma classe `dark:` foi usada. Explique como isso funciona.
4. Abra um contrato e alterne entre "Documento" e "Trechos". Encontre no código onde a sobreposição entre chunks é removida.
5. Faça uma busca, depois outra, e use o botão voltar do navegador. Por que a busca anterior volta?

---

## Problemas conhecidos

Encontrados lendo e rodando o código. Bons candidatos para as primeiras modificações.

### Já corrigidos

| Problema | O que era |
|---|---|
| Página Contratos vazia | A listagem consultava o Pinecone com um vetor de zeros. Com a métrica cosine, a similaridade com o vetor zero é indefinida (divisão por zero), e o Pinecone não devolve nada. Agora usa `index.list()` + `fetch()` |
| `pip install` falhava | `pinecone-client==5.4.2` não existe; o pacote passou a se chamar `pinecone` |
| Só funcionava com OpenAI | Criado `ai_config.py` para aceitar qualquer provedor compatível |
| Rodapé sem função | Links apontavam para `/` e o botão "API" não exibia nada. Removido |
| Dependências não usadas | `sentence-transformers` (PyTorch), `einops`, `pymongo`, `pdfplumber` removidos |
| `node_modules` versionado | 5.317 arquivos de dependências estavam no git. Removidos e ignorados; `npm install` recria |
| `frontend/.env` | Apontava para portas erradas e nunca era lido. Removido |
| Frontend refeito | Página "Sobre" e DaisyUI removidos; biblioteca mostra contratos (não chunks); tela de upload; Markdown do LLM renderizado e sanitizado; modo pergunta na página inicial; lista não é mais carregada duas vezes; botão de tema que comparava com `'britodark'` (tema inexistente) deixou de existir: o tema agora segue o sistema |

### Abertos

**Busca e RAG**

| Problema | Onde |
|---|---|
| O "enriquecimento" da consulta atrapalha perguntas com nome + valor, e tem nomes de pessoas fixos no código | `pinecone_utils.buscar_documentos` |
| A busca do `/contratos/busca` e a do `/llm/ask` são implementações diferentes | `api_pinecone.py` × `pinecone_utils.py` |
| `identificar_secao` classifica mal (a primeira palavra-chave vence) | `processar_contrato.py` |
| Metadados `valores_monetarios`, `cpfs`, `nomes` são lidos mas nunca gravados | `pinecone_utils.py` × `processar_contrato.py` |
| Upsert de um chunk por vez (lento) | `processar_contrato.py` |
| `inicializar_pinecone()` abre conexão nova a cada pergunta | `pinecone_utils.py` |
| `openrouter/free` sorteia um modelo grátis a cada chamada; às vezes cai num modelo classificador de segurança, que responde `User Safety: unsafe` em vez de uma resposta. Fixar um modelo específico em `AI_MODEL` resolve | `.env` |

**Código**

| Problema | Onde |
|---|---|
| Conexão ao Pinecone e `gerar_embedding` duplicados em 3 arquivos | `api_pinecone.py`, `pinecone_utils.py`, `processar_contrato.py` |
| `shared.py` não é usado; modelos Pydantic duplicados | `shared.py`, `api_pinecone.py` |
| `listar_todos_documentos` e `processar_e_indexar_documento` não são usados (e o primeiro ainda tem o bug do vetor de zeros) | `pinecone_utils.py` |
| O `HTTPException(404)` de "nenhum documento" é capturado pelo `except Exception` logo abaixo e vira 500 | `llm_router.py` |
| `sys.exit()` ao importar se faltar chave derruba quem importa (a API de upload) | `processar_contrato.py` |
| O nome do arquivo enviado é usado direto no caminho de destino (um nome como `../x.pdf` sairia da pasta) | `api_upload.py` |

**Frontend**

| Problema | Onde |
|---|---|
| A listagem mostra chunks como se fossem contratos ("132 contratos") | `contratos/+page.svelte` |
| A página do contrato baixa todos os chunks do índice para filtrar um contrato | `api.ts` (`listarTrechos`) |
| URLs da API fixas no código; os proxies do Vite não têm efeito | `api.ts`, `vite.config.js` |
