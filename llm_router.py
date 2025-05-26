from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from openai import OpenAI
import os
import time
from shared import buscar_contratos

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class QuestionRequest(BaseModel):
    question: str
    max_results: int = 50

class QuestionResponse(BaseModel):
    answer: str
    sources: List[dict]

@router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Responde a perguntas sobre contratos usando o LLM com base nos resultados da busca semântica."""
    start_time = time.time()
    
    try:
        # Validação básica da pergunta
        if not request.question or not request.question.strip():
            raise HTTPException(status_code=400, detail="A pergunta não pode estar vazia")
            
        print(f"[LLM] Recebida pergunta: '{request.question}' (max_results={request.max_results})")
        
        # 1. Busca direta no Pinecone usando a função buscar_documentos
        # IMPORTANTE: Contornando a função buscar_contratos para evitar incompatibilidade de formatos
        from pinecone_utils import buscar_documentos
        
        print(f"[LLM] Realizando busca semântica direta...")
        try:
            # Busca direta nos documentos
            documentos = buscar_documentos(request.question, request.max_results)
            
            # Verifica se há resultados
            if not documentos or len(documentos) == 0:
                print(f"[LLM] Nenhum documento relevante encontrado.")
                raise HTTPException(status_code=404, detail="Nenhum documento relevante encontrado.")
            
            print(f"[LLM] Encontrados {len(documentos)} documentos relevantes.")
        except Exception as e:
            print(f"[LLM] Erro na busca: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao processar a consulta: {str(e)}")
        
        # 3. Prepara contexto para o LLM diretamente dos documentos encontrados
        context = "\n\n".join(
            f"[Documento {i+1} - {doc['arquivo']}]\n{doc['texto']}"
            for i, doc in enumerate(documentos)
        )

        # 4. Geração da resposta com o LLM
        modelo = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        print(f"[LLM] Gerando resposta com o modelo {modelo}...")
        
        try:
            resposta_final = client.chat.completions.create(
                model=modelo,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente especializado em contratos imobiliários com acesso a uma base de documentos. "
                                   "Suas respostas devem ser:"
                                   "\n1. DETALHADAS - Forneça informações completas e abrangentes sobre o que foi perguntado."
                                   "\n2. ESPECÍFICAS - Quando a pergunta for sobre pessoas, entidades ou cláusulas, inclua TODOS os detalhes disponíveis nos documentos."
                                   "\n3. ESTRUTURADAS - Organize a resposta de forma clara, usando listas ou seções quando apropriado."
                                   "\n4. BASEADAS EM EVIDÊNCIAS - Cite explicitamente de qual documento/contrato a informação foi extraída."
                                   "\n. Cite explicitamente codigos de barras, caso as informações sejam de boletos de cobrança."
                    },
                    {
                        "role": "user",
                        "content": f"Documentos:\n{context}\n\nPergunta: {request.question}"
                    }
                ],
                temperature=0.5
            )
            
            answer = resposta_final.choices[0].message.content
        except Exception as e:
            print(f"[LLM] Erro ao gerar resposta: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro ao gerar resposta. Tente novamente.")

        # 5. Prepara e retorna a resposta diretamente dos documentos
        response = {
            "answer": answer,
            "sources": [{
                "filename": doc["arquivo"],
                "text": doc["texto"]
            } for doc in documentos]
        }
        
        elapsed_time = time.time() - start_time
        print(f"[LLM] Resposta gerada em {elapsed_time:.2f} segundos.")
        
        return response
        
    except HTTPException as e:
        # Repassa exceções HTTP
        raise
    except Exception as e:
        print(f"[LLM] Erro ao processar pergunta: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar pergunta: {str(e)}")
