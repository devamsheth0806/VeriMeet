import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface BotCreationRequest {
  meeting_url: string;
  bot_name?: string;
}

export interface BotCreationResponse {
  success: boolean;
  bot_id?: string;
  status?: string;
  meeting_url?: string;
  error?: string;
}

export interface SummaryResponse {
  success: boolean;
  summary?: string;
  error?: string;
}

export interface HealthResponse {
  status: string;
  service: string;
}

export const apiClient = {
  // Health check
  async getHealth(): Promise<HealthResponse> {
    const response = await api.get<HealthResponse>('/');
    return response.data;
  },

  // Create bot and send to meeting
  async createBot(data: BotCreationRequest): Promise<BotCreationResponse> {
    const response = await api.post<BotCreationResponse>('/api/create-bot', data);
    return response.data;
  },

  // Get current summary
  async getSummary(): Promise<SummaryResponse> {
    const response = await api.get<SummaryResponse>('/api/summary');
    return response.data;
  },
};

export default apiClient;

