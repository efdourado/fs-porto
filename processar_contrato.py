import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
import time
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

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
EMBEDDING_MODEL = "text-embedding-3-small"

# Verifica se as chaves estão configuradas
if not PINECONE_API_KEY:
    print("ERRO: PINECONE_API_KEY não encontrada no arquivo .env")
    sys.exit(1)

if not PINECONE_HOST:
    print("ERRO: PINECONE_HOST não encontrado no arquivo .env")
    sys.exit(1)
    
if not OPENAI_API_KEY:
    print("ERRO: OPENAI_API_KEY não encontrada no arquivo .env")
    sys.exit(1)

def gerar_embedding(texto):
    """Gera um embedding usando o modelo da OpenAI."""
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.embeddings.create(
            input=texto,
            model=EMBEDDING_MODEL
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Erro ao gerar embedding: {e}")
        raise

def inicializar_pinecone():
    """Inicializa a conexão com o Pinecone e retorna o índice."""
    try:
        # Inicializa o cliente Pinecone com a API V2
        pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # Conecta ao índice com o host específico
        index = pc.Index(PINECONE_INDEX_NAME, host=PINECONE_HOST)
        
        # Verifica se o índice está acessível obtendo suas estatísticas
        stats = index.describe_index_stats()
        print(f"Conexão com o índice '{PINECONE_INDEX_NAME}' estabelecida com sucesso!")
        print(f"Total de vetores no índice: {stats.get('total_vector_count', 0)}")
        
        return index
    
    except Exception as e:
        print(f"Erro ao inicializar Pinecone: {e}")
        sys.exit(1)

def processar_contrato(caminho_pdf):
    """
    Processa um único contrato PDF e o indexa no Pinecone.
    
    Args:
        caminho_pdf: Caminho completo para o arquivo PDF
        
    Returns:
        int: Número de chunks processados
    """
    if not os.path.exists(caminho_pdf):
        print(f"ERRO: Arquivo {caminho_pdf} não encontrado!")
        return 0
    
    if not caminho_pdf.lower().endswith('.pdf'):
        print(f"ERRO: Arquivo {caminho_pdf} não é um PDF!")
        return 0
    
    nome_arquivo = os.path.basename(caminho_pdf)
    print(f"Processando contrato: {nome_arquivo}")
    
    # Inicializa o Pinecone
    index = inicializar_pinecone()
    
    try:
        # Carrega o PDF
        loader = PyPDFLoader(caminho_pdf)
        dados = loader.load()
        
        # Divide em chunks de forma mais inteligente usando separadores específicos para contratos
        splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", "CLÁUSULA", "Cláusula", "ARTIGO", "Artigo", ". ", " ", ""],
            chunk_size=500,  # Chunks um pouco maiores para capturar mais contexto
            chunk_overlap=50  # Maior sobreposição para manter a coerência entre chunks
        )
        documentos = splitter.split_documents(dados)
        
        print(f"Contrato dividido em {len(documentos)} chunks usando chunking semântico")
        
        # Detecta possíveis seções do contrato
        def identificar_secao(texto):
            texto_lower = texto.lower()
            if any(termo in texto_lower for termo in ["locador", "proprietário", "senhorio"]):
                return "Identificação do Locador"
            elif any(termo in texto_lower for termo in ["locatário", "inquilino", "arrendatário"]):
                return "Identificação do Locatário"
            elif any(termo in texto_lower for termo in ["objeto", "imóvel", "endereço", "localização"]):
                return "Objeto do Contrato"
            elif any(termo in texto_lower for termo in ["aluguel", "valor", "pagamento", "preço", "reajuste"]):
                return "Condições de Pagamento"
            elif any(termo in texto_lower for termo in ["prazo", "vigência", "duração", "término"]):
                return "Prazo Contratual"
            elif any(termo in texto_lower for termo in ["rescisão", "multa", "penalidade", "quebra"]):
                return "Rescisão Contratual"
            elif any(termo in texto_lower for termo in ["garantia", "fiador", "caução", "depósito"]):
                return "Garantias Contratuais"
            else:
                return "Outras Cláusulas"
        
        # Processa cada chunk
        for i, doc in enumerate(documentos):
            texto = doc.page_content
            
            # Metadados enriquecidos
            metadata = {
                "arquivo": nome_arquivo,
                "texto": texto,
                "pagina": doc.metadata.get("page", 0),
                "secao": identificar_secao(texto),
                "tamanho_chunk": len(texto),
                "posicao": i,
                "total_chunks": len(documentos),
                "data_processamento": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Gera um ID único
            id = f"{nome_arquivo.replace('.pdf', '')}_{i}"
            
            # Gera o embedding
            embedding = gerar_embedding(texto)
            
            # Upsert no Pinecone
            index.upsert(vectors=[(id, embedding, metadata)])
            
            print(f"  Chunk {i+1}/{len(documentos)} processado")
        
        print(f"Contrato {nome_arquivo} processado com sucesso!")
        return len(documentos)
        
    except Exception as e:
        print(f"ERRO ao processar contrato {nome_arquivo}: {e}")
        return 0

def processar_pasta_contratos(pasta="./contratos"):
    """
    Processa todos os PDFs na pasta de contratos.
    
    Args:
        pasta: Caminho para a pasta de contratos
        
    Returns:
        int: Número total de contratos processados
    """
    if not os.path.exists(pasta):
        print(f"ERRO: Pasta {pasta} não encontrada!")
        return 0
    
    print(f"Processando contratos da pasta: {pasta}")
    
    total_contratos = 0
    total_chunks = 0
    
    for nome_arquivo in os.listdir(pasta):
        if nome_arquivo.lower().endswith('.pdf'):
            caminho_completo = os.path.join(pasta, nome_arquivo)
            chunks = processar_contrato(caminho_completo)
            
            if chunks > 0:
                total_contratos += 1
                total_chunks += chunks
    
    print(f"\nProcessamento concluído!")
    print(f"Total de contratos processados: {total_contratos}")
    print(f"Total de chunks indexados: {total_chunks}")
    
    return total_contratos

if __name__ == "__main__":
    # Se um arquivo específico foi fornecido como argumento
    if len(sys.argv) > 1:
        caminho_arquivo = sys.argv[1]
        processar_contrato(caminho_arquivo)
    else:
        # Processa todos os contratos na pasta
        processar_pasta_contratos()
