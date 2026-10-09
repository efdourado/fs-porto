# Exemplos

| Arquivo | Conteúdo |
|---|---|
| [`requisicoes.http`](requisicoes.http) | Todas as rotas das duas APIs, prontas para rodar no VS Code com a extensão REST Client |
| [`respostas/`](respostas/) | Respostas reais de cada rota, capturadas com os 12 contratos de exemplo indexados (textos longos cortados em 300 caracteres) |

| Resposta | Rota |
|---|---|
| [`status.json`](respostas/status.json) | `GET :8000/` |
| [`contratos-lista.json`](respostas/contratos-lista.json) | `GET :8000/contratos?skip=0&limit=2` |
| [`contratos-busca.json`](respostas/contratos-busca.json) | `GET :8000/contratos/busca?q=multa por rescisão&limit=3` |
| [`contratos-arquivos.json`](respostas/contratos-arquivos.json) | `GET :8000/contratos/arquivos` |
| [`llm-ask.json`](respostas/llm-ask.json) | `POST :8000/llm/ask` (exemplo de **falha de recuperação**, veja [05 · API](../docs/05-api.md#post-llmask)) |
| [`upload-lista.json`](respostas/upload-lista.json) | `GET :8001/contratos/lista` |

O arquivo de configuração de exemplo é o [`.env.example`](../.env.example), na raiz.
