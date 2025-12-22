import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import { API_CONFIG } from '../config/api';

// Types
export interface Memory {
  id?: string;
  title: string;
  content: string;
  category?: string;
  tags?: string[];
  created_at?: string;
  updated_at?: string;
  is_important?: boolean;
  reminder_date?: string;
  voice_file?: string;
  image?: string;
}

export interface User {
  id: string;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  timezone?: string;
  language?: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

// API Service Class
class ApiService {
  private api: AxiosInstance;
  private isOnline: boolean = true;
  private pendingRequests: Array<() => void> = [];

  constructor() {
    this.api = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
    this.setupNetworkListener();
  }

  // Setup axios interceptors
  private setupInterceptors() {
    // Request interceptor - add auth token
    this.api.interceptors.request.use(
      async (config) => {
        const token = await this.getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - handle token refresh
    this.api.interceptors.response.use(
      (response: AxiosResponse) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as any;
        
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            const newToken = await this.refreshToken();
            if (newToken) {
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
              return this.api(originalRequest);
            }
          } catch (refreshError) {
            await this.logout();
            throw refreshError;
          }
        }
        
        return Promise.reject(error);
      }
    );
  }

  // Network connectivity listener
  private setupNetworkListener() {
    NetInfo.addEventListener((state) => {
      const wasOffline = !this.isOnline;
      this.isOnline = state.isConnected ?? false;
      
      if (wasOffline && this.isOnline) {
        // Came back online - process pending requests
        this.processPendingRequests();
      }
    });
  }

  // Process pending requests when back online
  private async processPendingRequests() {
    const requests = [...this.pendingRequests];
    this.pendingRequests = [];
    
    for (const request of requests) {
      try {
        await request();
      } catch (error) {
        console.error('Failed to process pending request:', error);
      }
    }
  }

  // Token management
  private async getAccessToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem('access_token');
    } catch (error) {
      console.error('Error getting access token:', error);
      return null;
    }
  }

  private async setAccessToken(token: string): Promise<void> {
    try {
      await AsyncStorage.setItem('access_token', token);
    } catch (error) {
      console.error('Error setting access token:', error);
    }
  }

  private async getRefreshToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem('refresh_token');
    } catch (error) {
      console.error('Error getting refresh token:', error);
      return null;
    }
  }

  private async setRefreshToken(token: string): Promise<void> {
    try {
      await AsyncStorage.setItem('refresh_token', token);
    } catch (error) {
      console.error('Error setting refresh token:', error);
    }
  }

  private async refreshToken(): Promise<string | null> {
    try {
      const refreshToken = await this.getRefreshToken();
      if (!refreshToken) return null;

      const response = await axios.post(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.REFRESH_TOKEN}`, {
        refresh: refreshToken,
      });

      const { access } = response.data;
      await this.setAccessToken(access);
      return access;
    } catch (error) {
      console.error('Error refreshing token:', error);
      return null;
    }
  }

  // Authentication methods
  async login(username: string, password: string): Promise<AuthResponse> {
    try {
      const response = await this.api.post<AuthResponse>(API_CONFIG.ENDPOINTS.LOGIN, {
        username,
        password,
      });

      const { access, refresh, user } = response.data;
      await this.setAccessToken(access);
      await this.setRefreshToken(refresh);
      await AsyncStorage.setItem('user', JSON.stringify(user));

      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async register(userData: {
    username: string;
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
  }): Promise<AuthResponse> {
    try {
      const response = await this.api.post<AuthResponse>(API_CONFIG.ENDPOINTS.REGISTER, userData);

      const { access, refresh, user } = response.data;
      await this.setAccessToken(access);
      await this.setRefreshToken(refresh);
      await AsyncStorage.setItem('user', JSON.stringify(user));

      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async logout(): Promise<void> {
    try {
      await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user']);
    } catch (error) {
      console.error('Error during logout:', error);
    }
  }

  // Memory methods
  async getMemories(): Promise<Memory[]> {
    try {
      const response = await this.api.get<Memory[]>(API_CONFIG.ENDPOINTS.MEMORIES);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getMemory(id: string): Promise<Memory> {
    try {
      const response = await this.api.get<Memory>(API_CONFIG.ENDPOINTS.MEMORY_DETAIL(id));
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async createMemory(memory: Omit<Memory, 'id'>): Promise<Memory> {
    try {
      const response = await this.api.post<Memory>(API_CONFIG.ENDPOINTS.CREATE_MEMORY, memory);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async updateMemory(id: string, memory: Partial<Memory>): Promise<Memory> {
    try {
      const response = await this.api.put<Memory>(API_CONFIG.ENDPOINTS.UPDATE_MEMORY(id), memory);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async deleteMemory(id: string): Promise<void> {
    try {
      await this.api.delete(API_CONFIG.ENDPOINTS.DELETE_MEMORY(id));
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // AI Features
  async getAISuggestions(content: string): Promise<string[]> {
    try {
      const response = await this.api.post<{ suggestions: string[] }>(API_CONFIG.ENDPOINTS.AI_SUGGESTIONS, {
        content,
      });
      return response.data.suggestions;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async categorizeMemory(content: string): Promise<string> {
    try {
      const response = await this.api.post<{ category: string }>(API_CONFIG.ENDPOINTS.AI_CATEGORIZE, {
        content,
      });
      return response.data.category;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Voice features
  async uploadVoiceFile(uri: string): Promise<{ file_url: string }> {
    try {
      const formData = new FormData();
      formData.append('voice_file', {
        uri,
        type: 'audio/m4a',
        name: 'voice_recording.m4a',
      } as any);

      const response = await this.api.post<{ file_url: string }>(
        API_CONFIG.ENDPOINTS.VOICE_UPLOAD,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async transcribeVoice(voiceFileUrl: string): Promise<{ text: string }> {
    try {
      const response = await this.api.post<{ text: string }>(API_CONFIG.ENDPOINTS.VOICE_TRANSCRIBE, {
        voice_file: voiceFileUrl,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // User profile
  async getUserProfile(): Promise<User> {
    try {
      const response = await this.api.get<User>(API_CONFIG.ENDPOINTS.PROFILE);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async updateUserProfile(userData: Partial<User>): Promise<User> {
    try {
      const response = await this.api.put<User>(API_CONFIG.ENDPOINTS.UPDATE_PROFILE, userData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Sync methods
  async syncOfflineData(offlineData: any[]): Promise<{ success: boolean; synced_count: number }> {
    try {
      const response = await this.api.post<{ success: boolean; synced_count: number }>(
        API_CONFIG.ENDPOINTS.OFFLINE_SYNC,
        { offline_data: offlineData }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Error handling
  private handleError(error: any): Error {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.message || error.response.data?.detail || 'Server error';
      return new Error(message);
    } else if (error.request) {
      // Network error
      return new Error('Network error. Please check your connection.');
    } else {
      // Other error
      return new Error(error.message || 'An unexpected error occurred');
    }
  }

  // Check if user is authenticated
  async isAuthenticated(): Promise<boolean> {
    try {
      const token = await this.getAccessToken();
      return !!token;
    } catch (error) {
      return false;
    }
  }

  // Get current user
  async getCurrentUser(): Promise<User | null> {
    try {
      const userStr = await AsyncStorage.getItem('user');
      return userStr ? JSON.parse(userStr) : null;
    } catch (error) {
      return null;
    }
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;






