from fastapi import HTTPException
from pydantic import BaseModel
from typing import List
from pinecone_utils import buscar_documentos

class ContratoResponse(BaseModel):
    arquivo: str
    texto: str
    score: float = 0.0

class SearchResponse(BaseModel):
    resultados: List[ContratoResponse]
    total: int

def buscar_contratos(q: str, limit: int = 50):
    """
    Função compartilhada para busca de contratos
    """
    # Validação da consulta
    if not q or not q.strip():
        print("Erro: consulta vazia enviada para buscar_contratos")
        raise HTTPException(status_code=400, detail="A consulta não pode estar vazia")
    
    print(f"Iniciando busca de contratos para: '{q[:50]}...' (limit={limit})")
    
    try:
        # Realiza a busca semântica com tratamento de exceções específicas
        try:
            documentos = buscar_documentos(q, limit)
        except ValueError as ve:
            print(f"Erro de validação na busca de documentos: {ve}")
            raise HTTPException(status_code=400, detail=f"Erro na consulta: {str(ve)}")
        except ConnectionError as ce:
            print(f"Erro de conexão na busca de documentos: {ce}")
            raise HTTPException(status_code=503, detail=f"Serviço indisponível: {str(ce)}")
        except Exception as e:
            print(f"Erro inesperado na busca de documentos: {e}")
            raise HTTPException(status_code=500, detail=f"Erro interno ao processar a consulta: {str(e)}")
        
        # Verifica se documentos é uma lista válida
        if documentos is None:
            print("Erro: buscar_documentos retornou None")
            raise HTTPException(status_code=500, detail="Erro interno: resultado nulo da busca")
            
        if not isinstance(documentos, list):
            print(f"Erro: buscar_documentos retornou um formato inesperado: {type(documentos)}")
            raise HTTPException(status_code=500, detail=f"Erro interno: formato inválido ({type(documentos).__name__})")
        
        # Verifica se há resultados
        if len(documentos) == 0:
            print(f"Nenhum resultado encontrado para a consulta: '{q[:50]}...'")
            return SearchResponse(resultados=[], total=0)
        
        print(f"Processando {len(documentos)} documentos encontrados")
        
        # Processa os resultados
        resultados = []
        for i, doc in enumerate(documentos):
            try:
                # Verifica se doc é um dicionário
                if not isinstance(doc, dict):
                    print(f"Aviso: documento {i} em formato inesperado: {type(doc)}")
                    continue
                
                # Verifica campos obrigatórios
                arquivo = doc.get("arquivo")
                texto = doc.get("texto")
                score = doc.get("score", 0.0)
                
                if not arquivo or not texto:
                    print(f"Aviso: documento {i} com campos obrigatórios ausentes: {doc}")
                    continue
                
                # Converte score para float se necessário
                if not isinstance(score, (int, float)):
                    try:
                        score = float(score)
                    except (ValueError, TypeError):
                        print(f"Aviso: score inválido no documento {i}: {score}")
                        score = 0.0
                
                # Cria o objeto de resposta
                resultados.append(ContratoResponse(
                    arquivo=arquivo,
                    texto=texto,
                    score=score
                ))
            except Exception as e:
                print(f"Erro ao processar documento {i}: {e}")
                continue
        
        # Verifica se algum resultado foi processado com sucesso
        if not resultados:
            print("Aviso: nenhum documento válido encontrado após processamento")
            return SearchResponse(resultados=[], total=0)
        
        total = len(resultados)
        print(f"Busca concluída com sucesso: {total} resultados válidos")
        
        return SearchResponse(resultados=resultados, total=total)
    
    except HTTPException:
        # Repassa exceções HTTP já formatadas
        raise
    except Exception as e:
        print(f"Erro detalhado na busca de contratos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao realizar a busca: {str(e)}")
