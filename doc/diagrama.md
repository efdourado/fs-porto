# Diagrama de Arquitetura - Contratus AI Imobiliária

```mermaid
graph TD
    User[Usuário]
    PDF[Arquivos PDF de Contratos]
    UploadAPI[API de Upload]
    Processor[Processador de Contratos]
    PineconeAPI[API de Busca Semântica]
    PineconeUtils[Utilitários Pinecone]
    OpenAI[OpenAI API]
    PineconeDB[(Pinecone DB)]
    Frontend[Frontend SvelteKit]
    
    User -->|1. Faz upload de contrato| Frontend
    Frontend -->|2. Envia PDF| UploadAPI
    UploadAPI -->|3. Salva PDF| PDF
    UploadAPI -->|4. Inicia processamento| Processor
    
    Processor -->|5. Carrega PDF| PDF
    Processor -->|6. Divide em chunks| Processor
    Processor -->|7. Solicita embeddings| OpenAI
    OpenAI -->|8. Retorna embeddings| Processor
    Processor -->|9. Armazena vetores| PineconeDB
    
    User -->|10. Faz consulta| Frontend
    Frontend -->|11. Envia consulta| PineconeAPI
    PineconeAPI -->|12. Solicita embedding| OpenAI
    OpenAI -->|13. Retorna embedding| PineconeAPI
    PineconeAPI -->|14. Busca vetores| PineconeDB
    PineconeDB -->|15. Retorna resultados| PineconeAPI
    PineconeAPI -->|16. Envia resultados| Frontend
    Frontend -->|17. Exibe resultados| User
    
    classDef api fill:#f9f,stroke:#333
    classDef processor fill:#bbf,stroke:#333
    classDef database fill:#bfb,stroke:#333
    classDef frontend fill:#fbb,stroke:#333
    classDef external fill:#ddd,stroke:#333
    
    class UploadAPI,PineconeAPI api
    class Processor,PineconeUtils processor
    class PineconeDB,PDF database
    class Frontend frontend
    class OpenAI external
```

## Arquivos do Sistema

| Componente | Arquivo | Descrição |
|-----------|---------|------------|
| API de Upload | `api_upload.py` | Recebe e processa uploads de contratos |
| API de Busca | `api_pinecone.py` | Realiza buscas semânticas nos contratos |
| Processador | `processar_contrato.py` | Extrai texto, divide em chunks e gera embeddings |
| Utilitários | `pinecone_utils.py` | Funções auxiliares para interação com Pinecone |

## Fluxo de Processamento de Contratos

1. O usuário faz upload de um contrato PDF através do frontend SvelteKit
2. A API de Upload recebe o arquivo e o salva na pasta de contratos
3. O Processador de Contratos é acionado em segundo plano para:
   - Carregar o PDF e extrair o texto
   - Dividir o texto em chunks menores
   - Gerar embeddings para cada chunk usando a OpenAI
   - Armazenar os vetores e metadados no Pinecone

## Fluxo de Consulta Semântica

1. O usuário faz uma consulta em linguagem natural através do frontend
2. A API de Busca Semântica recebe a consulta e:
   - Gera um embedding para a consulta usando a OpenAI
   - Busca os vetores mais similares no Pinecone
   - Retorna os resultados ordenados por relevância
3. O frontend exibe os resultados ao usuário
