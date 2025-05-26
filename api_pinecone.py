import os
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from pinecone import Pinecone

# Obtém o caminho absoluto do diretório atual
diretorio_atual = os.path.dirname(os.path.abspath(__file__))

# Carrega as variáveis de ambiente do arquivo .env no diretório atual
env_path = os.path.join(diretorio_atual, '.env')
load_dotenv(dotenv_path=env_path)

# Configurações do Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_HOST = os.getenv("PINECONE_HOST")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "brito-ai")

# Configurações da OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)
EMBEDDING_MODEL = "text-embedding-3-small"

# Variáveis globais para conexão com Pinecone
pc = None
index = None
connection_attempts = 0
MAX_RECONNECT_ATTEMPTS = 3

def conectar_pinecone():
    """Função para conectar ao Pinecone com retry automático"""
    global pc, index, connection_attempts
    
    try:
        # Inicializa o cliente Pinecone com a API V2
        pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # Conecta ao índice com o host específico
        index = pc.Index(PINECONE_INDEX_NAME, host=PINECONE_HOST)
        
        # Verifica se o índice está acessível obtendo suas estatísticas
        stats = index.describe_index_stats()
        print(f"Conexão com o índice '{PINECONE_INDEX_NAME}' estabelecida com sucesso!")
        print(f"Total de vetores no índice: {stats.get('total_vector_count', 0)}")
        
        # Resetar contador de tentativas após sucesso
        connection_attempts = 0
        return True
        
    except Exception as e:
        connection_attempts += 1
        print(f"Erro ao inicializar Pinecone (tentativa {connection_attempts}/{MAX_RECONNECT_ATTEMPTS}): {e}")
        
        if connection_attempts < MAX_RECONNECT_ATTEMPTS:
            import time
            print(f"Tentando reconectar em 2 segundos...")
            time.sleep(2)
            return conectar_pinecone()
        else:
            print("Número máximo de tentativas excedido. Falha na conexão com Pinecone.")
            return False

# Inicializa a conexão com Pinecone
conexao_bem_sucedida = conectar_pinecone()

# Função para gerar embeddings
def gerar_embedding(texto):
    """
    Gera um embedding usando o modelo da OpenAI.
    
    Args:
        texto: Texto para gerar o embedding
        
    Returns:
        Lista com o embedding
    """
    try:
        response = openai_client.embeddings.create(
            input=texto,
            model=EMBEDDING_MODEL
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Erro ao gerar embedding: {e}")
        raise

# Inicializa o FastAPI
app = FastAPI(title="Contratus AI API", 
              description="API para consulta semântica de contratos usando Pinecone",
              version="2.0.0")

# Importação segura após definição de todas as classes/funções
from llm_router import router as llm_router
app.include_router(llm_router, prefix="/llm", tags=["LLM"])

# Configuração de CORS para permitir requisições do frontend e do proxy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Modelos de dados
class ContratoBase(BaseModel):
    arquivo: str
    texto: str

class ContratoResponse(ContratoBase):
    score: float = 0.0
    
class SearchResponse(BaseModel):
    resultados: List[ContratoResponse]
    total: int

@app.get("/")
def read_root():
    # Verifica se a conexão com Pinecone está ativa
    global index
    
    try:
        if index:
            # Tenta uma operação simples para verificar a conexão
            stats = index.describe_index_stats()
            return {
                "status": "online", 
                "message": "Contratus AI API está funcionando com Pinecone!",
                "pinecone_status": "conectado",
                "total_vetores": stats.get("total_vector_count", 0)
            }
        else:
            # Tenta reconectar
            if conectar_pinecone():
                return {
                    "status": "online", 
                    "message": "Contratus AI API está funcionando com Pinecone!",
                    "pinecone_status": "reconectado"
                }
            else:
                return {
                    "status": "parcial", 
                    "message": "API está online, mas sem conexão com Pinecone.",
                    "pinecone_status": "desconectado"
                }
    except Exception as e:
        # Tenta reconectar em caso de erro
        conectar_pinecone()
        return {
            "status": "degradado", 
            "message": "API está online, mas com problemas de conexão ao Pinecone.",
            "error": str(e)
        }

@app.get("/contratos", response_model=SearchResponse)
def listar_contratos(
    skip: int = Query(0, description="Número de registros para pular"),
    limit: int = Query(10, description="Número máximo de registros para retornar")
):
    """
    Lista todos os contratos disponíveis com paginação.
    """
    global index
    
    # Verifica se a conexão com Pinecone está ativa
    if not index and not conectar_pinecone():
        raise HTTPException(
            status_code=503, 
            detail="Serviço temporariamente indisponível. Não foi possível conectar ao Pinecone."
        )
    
    try:
        # Obtém estatísticas do índice
        stats = index.describe_index_stats()
        total = stats.get("total_vector_count", 0)
        
        # Limitação: Pinecone não suporta paginação nativa como MongoDB
        # Vamos usar uma abordagem simplificada para demonstração
        # Em produção, você pode querer implementar uma solução mais robusta
        
        # Busca genérica para obter todos os documentos
        # Nota: Isso não é eficiente para grandes conjuntos de dados
        # Criamos um vetor de zeros com a dimensão correta (1536 para text-embedding-3-small)
        dummy_vector = [0.0] * 1536
        
        # Fazemos uma consulta com um limite alto
        resultados_query = index.query(
            vector=dummy_vector,
            top_k=skip + limit,
            include_metadata=True
        )
        
        # Aplica paginação manualmente
        matches = resultados_query.matches[skip:skip+limit] if resultados_query.matches else []
        
        resultados = []
        for match in matches:
            resultados.append(ContratoResponse(
                arquivo=match.metadata.get("arquivo", ""),
                texto=match.metadata.get("texto", ""),
                score=match.score
            ))
        
        return SearchResponse(resultados=resultados, total=total)
    
    except Exception as e:
        print(f"Erro ao listar contratos: {e}")
        
        # Tenta reconectar em caso de erro
        if conectar_pinecone():
            # Tenta novamente após reconexão bem-sucedida
            try:
                return listar_contratos(skip=skip, limit=limit)
            except Exception:
                pass
                
        raise HTTPException(status_code=500, detail=f"Erro ao listar contratos: {str(e)}")

@app.get("/contratos/busca", response_model=SearchResponse)
def buscar_contratos(
    q: str = Query(..., description="Consulta para busca"),
    limit: int = Query(5, description="Número máximo de resultados")
):
    """
    Realiza uma busca semântica nos contratos usando o Pinecone com embeddings da OpenAI.
    """
    global index
    
    if not q:
        raise HTTPException(status_code=400, detail="A consulta não pode estar vazia")
    
    # Verifica se a conexão com Pinecone está ativa
    if not index and not conectar_pinecone():
        raise HTTPException(
            status_code=503, 
            detail="Serviço temporariamente indisponível. Não foi possível conectar ao Pinecone."
        )
    
    try:
        # Gera o embedding da consulta usando o modelo da OpenAI
        query_embedding = gerar_embedding(q)
        
        # Realiza a busca vetorial no Pinecone
        resultados_query = index.query(
            vector=query_embedding,
            top_k=limit,
            include_metadata=True
        )
        
        resultados = []
        for match in resultados_query.matches:
            resultados.append(ContratoResponse(
                arquivo=match.metadata.get("arquivo", ""),
                texto=match.metadata.get("texto", ""),
                score=match.score
            ))
        
        total = len(resultados)
        
        return SearchResponse(resultados=resultados, total=total)
    
    except Exception as e:
        print(f"Erro na busca: {e}")
        
        # Tenta reconectar em caso de erro
        if conectar_pinecone():
            # Tenta novamente após reconexão bem-sucedida
            try:
                return buscar_contratos(q=q, limit=limit)
            except Exception:
                pass
                
        raise HTTPException(status_code=500, detail=f"Erro ao realizar a busca: {str(e)}")

@app.get("/contratos/arquivos")
def listar_arquivos():
    """
    Lista todos os nomes de arquivos únicos no índice.
    """
    global index
    
    # Verifica se a conexão com Pinecone está ativa
    if not index and not conectar_pinecone():
        raise HTTPException(
            status_code=503, 
            detail="Serviço temporariamente indisponível. Não foi possível conectar ao Pinecone."
        )
    
    try:
        # Obtém estatísticas do índice
        stats = index.describe_index_stats()
        total = stats.get("total_vector_count", 0)
        
        # Limitação: Pinecone não tem uma função direta para obter valores distintos
        # Vamos usar uma abordagem simplificada para demonstração
        
        # Busca genérica para obter documentos
        # Nota: Isso não é eficiente para grandes conjuntos de dados
        # Criamos um vetor de zeros com a dimensão correta (1536 para text-embedding-3-small)
        dummy_vector = [0.0] * 1536
        
        # Fazemos uma consulta com um limite alto
        resultados_query = index.query(
            vector=dummy_vector,
            top_k=min(total, 1000),  # Limita a 1000 para evitar problemas de performance
            include_metadata=True
        )
        
        # Extrai nomes de arquivos únicos
        arquivos = set()
        for match in resultados_query.matches:
            arquivo = match.metadata.get("arquivo")
            if arquivo:
                arquivos.add(arquivo)
        
        return {"arquivos": list(arquivos)}
    
    except Exception as e:
        print(f"Erro ao listar arquivos: {e}")
        
        # Tenta reconectar em caso de erro
        if conectar_pinecone():
            # Tenta novamente após reconexão bem-sucedida
            try:
                return listar_arquivos()
            except Exception:
                pass
                
        raise HTTPException(status_code=500, detail=f"Erro ao listar arquivos: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("api_pinecone:app", host="127.0.0.1", port=8000, reload=True)
