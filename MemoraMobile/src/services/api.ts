import axios, { AxiosInstance, AxiosResponse } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1'; // Update this to your Memora Core server URL

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth tokens
api.interceptors.request.use(
  async (config) => {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error('Error getting auth token:', error);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      await AsyncStorage.removeItem('auth_token');
      // You can add navigation to login screen here
    }
    return Promise.reject(error);
  }
);

// Auth API endpoints
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login/', { email, password }),
  
  register: (userData: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
  }) => api.post('/auth/register/', userData),
  
  logout: () => api.post('/auth/logout/'),
  
  refreshToken: (refresh: string) =>
    api.post('/auth/token/refresh/', { refresh }),
};

// Memory API endpoints
export const memoryAPI = {
  getMemories: (params?: {
    page?: number;
    search?: string;
    memory_type?: string;
    date_from?: string;
    date_to?: string;
  }) => api.get('/memories/', { params }),
  
  getMemory: (id: number) => api.get(`/memories/${id}/`),
  
  createMemory: (memoryData: {
    title: string;
    content: string;
    memory_type?: string;
    priority?: string;
    scheduled_date?: string;
  }) => api.post('/memories/', memoryData),
  
  updateMemory: (id: number, memoryData: any) =>
    api.put(`/memories/${id}/`, memoryData),
  
  deleteMemory: (id: number) => api.delete(`/memories/${id}/`),
  
  likeMemory: (id: number) => api.post(`/memories/${id}/like/`),
  
  unlikeMemory: (id: number) => api.delete(`/memories/${id}/like/`),
  
  addComment: (id: number, comment: string) =>
    api.post(`/memories/${id}/comments/`, { content: comment }),
};

// User API endpoints
export const userAPI = {
  getProfile: () => api.get('/users/profile/'),
  
  updateProfile: (profileData: any) =>
    api.put('/users/profile/', profileData),
  
  getFriends: () => api.get('/users/friends/'),
  
  searchUsers: (query: string) =>
    api.get('/users/search/', { params: { q: query } }),
};

// AI API endpoints
export const aiAPI = {
  getSuggestions: () => api.get('/ai/suggestions/'),
  
  enhanceMemory: (id: number) =>
    api.post(`/memories/${id}/enhance/`),
  
  categorizeMemory: (content: string) =>
    api.post('/ai/categorize/', { content }),
  
  getDashboardStats: () => api.get('/ai/dashboard-stats/'),
  
  getPersonalizedRecommendations: () => api.get('/ai/recommendations/'),
  
  getMemoryInsights: () => api.get('/ai/insights/'),
  
  autoEnhanceMemory: (memoryData: {
    content: string;
    memory_type?: string;
  }) => api.post('/ai/auto-enhance/', memoryData),
  
  semanticSearch: (query: string, options?: {
    limit?: number;
    min_relevance?: number;
    search_type?: 'semantic' | 'hybrid' | 'keyword';
  }) => api.post('/ai/semantic-search/', { query, ...options }),
  
  getSearchSuggestions: (query: string) =>
    api.get('/ai/search-suggestions/', { params: { q: query } }),
};

// Smart Reminders API
export const reminderAPI = {
  getReminders: () => api.get('/reminders/'),
  
  createReminder: (reminderData: {
    title: string;
    description: string;
    scheduled_date: string;
    reminder_type: string;
  }) => api.post('/reminders/', reminderData),
  
  updateReminder: (id: number, reminderData: any) =>
    api.put(`/reminders/${id}/`, reminderData),
  
  deleteReminder: (id: number) => api.delete(`/reminders/${id}/`),
};

// Social API endpoints
export const socialAPI = {
  getOrganizations: () => api.get('/social/organizations/'),
  
  createOrganization: (orgData: {
    name: string;
    description: string;
  }) => api.post('/social/organizations/', orgData),
  
  shareMemory: (memoryId: number, shareData: {
    organization_id?: number;
    user_ids?: number[];
  }) => api.post(`/memories/${memoryId}/share/`, shareData),
  
  getSharedMemories: () => api.get('/memories/shared/'),
};

// Voice and Audio API endpoints
export const voiceAPI = {
  transcribeAudio: (audioFile: FormData, language?: string) =>
    api.post('/voice/transcribe/', audioFile, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      params: { language },
    }),
  
  textToSpeech: (text: string, language?: string) =>
    api.post('/voice/tts/', { text, language }),
  
  createVoiceMemory: (audioData: {
    audio_file: FormData;
    transcription?: string;
    language?: string;
  }) => api.post('/voice/create-memory/', audioData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
  
  voiceSearch: (audioFile: FormData, language?: string) =>
    api.post('/voice/search/', audioFile, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      params: { language },
    }),
};

// Analytics and Dashboard API
export const analyticsAPI = {
  getDashboardData: () => api.get('/analytics/dashboard/'),
  
  getMemoryStats: (period?: 'week' | 'month' | 'year') =>
    api.get('/analytics/memory-stats/', { params: { period } }),
  
  getProductivityMetrics: () => api.get('/analytics/productivity/'),
  
  getMemoryPatterns: () => api.get('/analytics/patterns/'),
  
  getSentimentAnalysis: () => api.get('/analytics/sentiment/'),
  
  getTagAnalytics: () => api.get('/analytics/tags/'),
  
  getTimeAnalytics: () => api.get('/analytics/time-patterns/'),
};

// Language and Localization API
export const languageAPI = {
  detectLanguage: (text: string) =>
    api.post('/language/detect/', { text }),
  
  getUserLanguage: () => api.get('/language/user-preference/'),
  
  setUserLanguage: (language: string) =>
    api.post('/language/set-preference/', { language }),
  
  getSupportedLanguages: () => api.get('/language/supported/'),
  
  translateText: (text: string, targetLanguage: string) =>
    api.post('/language/translate/', { text, target_language: targetLanguage }),
};

export default api;




