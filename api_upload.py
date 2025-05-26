import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
from processar_contrato import processar_contrato

# Obtém o caminho absoluto do diretório atual
diretorio_atual = os.path.dirname(os.path.abspath(__file__))

# Carrega as variáveis de ambiente do arquivo .env no diretório atual
env_path = os.path.join(diretorio_atual, '.env')
load_dotenv(dotenv_path=env_path)

# Pasta para armazenar os contratos
PASTA_CONTRATOS = os.path.join(diretorio_atual, "contratos")

# Cria a pasta de contratos se não existir
if not os.path.exists(PASTA_CONTRATOS):
    os.makedirs(PASTA_CONTRATOS)

# Inicializa o FastAPI
app = FastAPI(title="Contratus AI Imobiliária API - Upload", 
              description="API para upload e processamento de contratos imobiliários",
              version="1.0.0")

# Configuração de CORS para permitir requisições do frontend e do proxy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas as origens para facilitar o desenvolvimento
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

def processar_contrato_background(caminho_arquivo: str):
    """Processa um contrato em segundo plano."""
    try:
        processar_contrato(caminho_arquivo)
    except Exception as e:
        print(f"Erro ao processar contrato em segundo plano: {e}")

@app.post("/upload/contrato")
async def upload_contrato(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Faz upload de um novo contrato PDF e o processa automaticamente.
    O processamento ocorre em segundo plano para não bloquear a resposta.
    """
    # Verifica se o arquivo é um PDF
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos")
    
    try:
        # Salva o arquivo na pasta de contratos
        caminho_destino = os.path.join(PASTA_CONTRATOS, file.filename)
        
        # Se o arquivo já existir, adiciona um timestamp ao nome
        if os.path.exists(caminho_destino):
            nome_base, extensao = os.path.splitext(file.filename)
            import time
            timestamp = int(time.time())
            novo_nome = f"{nome_base}_{timestamp}{extensao}"
            caminho_destino = os.path.join(PASTA_CONTRATOS, novo_nome)
        
        # Salva o arquivo
        with open(caminho_destino, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Processa o contrato em segundo plano
        background_tasks.add_task(processar_contrato_background, caminho_destino)
        
        return {
            "status": "success",
            "message": "Contrato enviado com sucesso e está sendo processado",
            "arquivo": os.path.basename(caminho_destino)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar o upload: {str(e)}")

@app.get("/contratos/lista")
async def listar_contratos():
    """
    Lista todos os contratos disponíveis na pasta de contratos.
    """
    try:
        contratos = []
        
        # Lista todos os arquivos PDF na pasta de contratos
        for arquivo in os.listdir(PASTA_CONTRATOS):
            if arquivo.lower().endswith('.pdf'):
                caminho_completo = os.path.join(PASTA_CONTRATOS, arquivo)
                tamanho = os.path.getsize(caminho_completo)
                data_modificacao = os.path.getmtime(caminho_completo)
                
                import time
                data_formatada = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data_modificacao))
                
                contratos.append({
                    "nome": arquivo,
                    "tamanho_bytes": tamanho,
                    "data_modificacao": data_formatada
                })
        
        return {"contratos": contratos, "total": len(contratos)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar contratos: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("api_upload:app", host="0.0.0.0", port=8001, reload=True)
