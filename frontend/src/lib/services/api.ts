import axios from 'axios';

// URL da API de busca (api_pinecone.py)
const API_URL = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000
});

export interface Contrato {
  arquivo: string;
  texto: string;
  score?: number;
}

export interface SearchResponse {
  resultados: Contrato[];
  total: number;
}

export interface LLMResponse {
  answer: string;
  sources: Array<{
    filename?: string;
    text?: string;
  }>;
}

// Extrai a mensagem de erro do FastAPI ({"detail": "..."}) ou uma mensagem amigável
function mensagemDeErro(error: any, padrao: string): string {
  if (error?.response?.data?.detail) return String(error.response.data.detail);
  if (error?.code === 'ECONNABORTED') return 'O servidor demorou demais para responder.';
  if (error?.request && !error?.response) return 'Não foi possível conectar à API. Ela está rodando na porta 8000?';
  return padrao;
}

export const contratoService = {
  // Lista os chunks indexados, com paginação
  listarContratos: async (skip = 0, limit = 10): Promise<SearchResponse> => {
    try {
      const response = await api.get('/contratos', { params: { skip, limit } });
      return response.data;
    } catch (error) {
      throw new Error(mensagemDeErro(error, 'Erro ao listar contratos.'));
    }
  },

  // Todos os chunks de um contrato, na ordem do documento
  listarTrechos: async (arquivo: string): Promise<Contrato[]> => {
    const { resultados } = await contratoService.listarContratos(0, 10000);
    return resultados.filter((r) => r.arquivo === arquivo);
  },

  // Busca semântica
  buscarContratos: async (query: string, limit = 8): Promise<SearchResponse> => {
    try {
      const response = await api.get('/contratos/busca', { params: { q: query, limit } });
      return response.data;
    } catch (error) {
      throw new Error(mensagemDeErro(error, 'Erro ao realizar a busca.'));
    }
  },

  // Nomes dos arquivos indexados
  listarArquivos: async (): Promise<string[]> => {
    try {
      const response = await api.get('/contratos/arquivos');
      return response.data.arquivos;
    } catch (error) {
      throw new Error(mensagemDeErro(error, 'Erro ao listar contratos.'));
    }
  },

  // Pergunta ao LLM (RAG)
  askQuestion: async (question: string, maxResults = 5): Promise<LLMResponse> => {
    const pergunta = question.trim().substring(0, 1000);
    if (!pergunta) throw new Error('A pergunta não pode estar vazia.');

    try {
      const response = await api.post(
        '/llm/ask',
        { question: pergunta, max_results: maxResults },
        { timeout: 60000 } // o LLM pode levar dezenas de segundos
      );
      return response.data;
    } catch (error) {
      throw new Error(mensagemDeErro(error, 'Erro ao processar a pergunta.'));
    }
  }
};

export default api;
