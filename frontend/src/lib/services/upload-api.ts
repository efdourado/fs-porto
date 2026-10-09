import axios from 'axios';

// URL da API de upload (api_upload.py)
const UPLOAD_API_URL = 'http://localhost:8001';

// Sem Content-Type fixo: com FormData, o navegador define multipart/form-data com o boundary correto
const uploadApi = axios.create({
  baseURL: UPLOAD_API_URL,
  timeout: 60000
});

export interface UploadResponse {
  status: string;
  message: string;
  arquivo: string;
}

export const uploadService = {
  // Envia um PDF; a indexação continua em segundo plano no servidor
  enviarContrato: async (arquivo: File): Promise<UploadResponse> => {
    const form = new FormData();
    form.append('file', arquivo);
    try {
      const response = await uploadApi.post('/upload/contrato', form);
      return response.data;
    } catch (error: any) {
      if (error?.response?.data?.detail) throw new Error(String(error.response.data.detail));
      throw new Error('Não foi possível enviar. A API de upload está rodando na porta 8001?');
    }
  }
};

export default uploadApi;
