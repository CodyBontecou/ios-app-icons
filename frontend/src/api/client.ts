import axios from 'axios';
import type {
  GenerateRequest,
  GenerateResponse,
  JobStatusResponse,
  ConfigResponse,
  HealthResponse,
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Generate icons
  generate: async (request: GenerateRequest): Promise<GenerateResponse> => {
    const response = await apiClient.post<GenerateResponse>('/generate', request);
    return response.data;
  },

  // Get job status
  getJobStatus: async (jobId: string): Promise<JobStatusResponse> => {
    const response = await apiClient.get<JobStatusResponse>(`/status/${jobId}`);
    return response.data;
  },

  // Get config
  getConfig: async (): Promise<ConfigResponse> => {
    const response = await apiClient.get<ConfigResponse>('/config');
    return response.data;
  },

  // Health check
  healthCheck: async (): Promise<HealthResponse> => {
    const response = await apiClient.get<HealthResponse>('/health');
    return response.data;
  },
};

export default api;
