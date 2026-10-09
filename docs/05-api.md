# 05 · Referência da API

Dois servidores FastAPI. Com eles rodando, a documentação interativa (Swagger, onde dá para testar cada rota no navegador) fica em:

- http://127.0.0.1:8000/docs (busca e perguntas)
- http://127.0.0.1:8001/docs (upload)

Requisições prontas para rodar estão em [`exemplos/requisicoes.http`](../exemplos/requisicoes.http), e as respostas reais completas em [`exemplos/respostas/`](../exemplos/respostas/).

## API de busca (porta 8000)

### `GET /`

Status da API e da conexão com o Pinecone.

```bash
curl http://127.0.0.1:8000/
```

```json
{
  "status": "online",
  "message": "Porto API está funcionando com Pinecone!",
  "pinecone_status": "conectado",
  "total_vetores": 132
}
```

`status` pode ser `online`, `parcial` (sem Pinecone) ou `degradado` (erro na conexão).

### `GET /contratos`

Lista os **chunks** indexados, ordenados por arquivo e posição, com paginação.

| Parâmetro | Padrão | Descrição |
|---|---|---|
| `skip` | 0 | Quantos chunks pular |
| `limit` | 10 | Quantos devolver |

```bash
curl "http://127.0.0.1:8000/contratos?skip=0&limit=2"
```

```json
{
  "resultados": [
    {
      "arquivo": "Contrato_Altos_Padroes_Construcoes_GR340_X_Bruno_Mendes_Oliveira.pdf",
      "texto": "CONTRATO DE LOCAÇÃO DE IMÓVEL\nIDENTIFICAÇÃO DAS PARTES CONTRATANTES\nLOCADOR: ...",
      "score": 0.0
    }
  ],
  "total": 132
}
```

`total` é o total de chunks no índice. `score` é sempre 0 aqui (não há consulta para comparar).

### `GET /contratos/busca`

Busca semântica: os chunks com significado mais próximo da consulta.

| Parâmetro | Padrão | Descrição |
|---|---|---|
| `q` | obrigatório | Texto da consulta |
| `limit` | 50 | Número de resultados (`top_k`). O frontend envia 5 |

```bash
curl "http://127.0.0.1:8000/contratos/busca?q=multa%20por%20rescis%C3%A3o&limit=3"
```

```json
{
  "resultados": [
    {
      "arquivo": "Contrato_Espaco_Urbano_Construtora_VS903_X_Carla_Ferreira_Santos.pdf",
      "texto": "RESCISÃO\nO presente contrato poderá ser rescindido antes do prazo, ... multa correspondente a 3 (três) meses de aluguel ...",
      "score": 0.514601707
    }
  ],
  "total": 3
}
```

`score` é a similaridade de cosseno (quanto maior, mais parecido). Repare que os três primeiros resultados são a **mesma cláusula** em contratos diferentes: os contratos seguem um modelo, então o texto é quase idêntico e os scores ficam muito próximos.

### `GET /contratos/arquivos`

Nomes únicos dos arquivos que têm chunks no índice.

```json
{ "arquivos": ["Contrato_Altos_Padroes_...pdf", "...", "Contrato_Viver_Bem_...pdf"] }
```

### `POST /llm/ask`

Pergunta em linguagem natural respondida pelo LLM com base nos chunks encontrados (RAG).

```bash
curl -X POST http://127.0.0.1:8000/llm/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Qual a multa por rescisão antecipada no contrato do Bruno Mendes Oliveira?", "max_results": 3}'
```

| Campo | Padrão | Descrição |
|---|---|---|
| `question` | obrigatório | A pergunta |
| `max_results` | 50 | Quantos chunks enviar ao LLM como contexto. O frontend envia 3 |

```json
{
  "answer": "Com base exclusivamente no trecho fornecido do Documento 3 (...Bruno_Mendes_Oliveira.pdf), não é possível informar a multa por rescisão antecipada. ...",
  "sources": [
    { "filename": "Contrato_Lar_Feliz_Imoveis_TP610_X_Fernando_Gomes_Ribeiro.pdf", "text": "...VALOR DO ALUGUEL..." }
  ]
}
```

Este exemplo é uma **falha real de recuperação**, guardada de propósito: a palavra "multa" ativa o enriquecimento de "valores" em `pinecone_utils.py`, a busca devolve cláusulas de pagamento e o LLM, corretamente, diz que não encontrou a informação. A cláusula de rescisão do Bruno existe no índice. Veja o exercício no [roteiro](06-roteiro-de-estudo.md).

Erros: `400` (pergunta vazia), `500` (falha na busca ou no LLM; mensagem em `detail`).

## API de upload (porta 8001)

### `POST /upload/contrato`

Envia um PDF. Ele é salvo em `contratos/` e indexado em segundo plano.

```bash
curl -X POST http://127.0.0.1:8001/upload/contrato -F "file=@caminho/contrato.pdf"
```

```json
{
  "status": "success",
  "message": "Contrato enviado com sucesso e está sendo processado",
  "arquivo": "contrato.pdf"
}
```

A resposta chega **antes** de a indexação terminar. Acompanhe o terminal do servidor para ver os chunks sendo processados; depois `GET :8000/` deve mostrar mais vetores. Erro `400` se o arquivo não for `.pdf`.

### `GET /contratos/lista`

Lista os PDFs da **pasta** `contratos/` (não do Pinecone).

```json
{
  "contratos": [
    {
      "nome": "Contrato_Altos_Padroes_Construcoes_GR340_X_Bruno_Mendes_Oliveira.pdf",
      "tamanho_bytes": 4352,
      "data_modificacao": "2025-06-19 18:21:55"
    }
  ],
  "total": 12
}
```
