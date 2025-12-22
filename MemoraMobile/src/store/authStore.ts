import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { authAPI } from '../services/api';
import { User, AuthState, LoginFormData, RegisterFormData } from '../types';

interface AuthStore extends AuthState {
  // Actions
  login: (credentials: LoginFormData) => Promise<void>;
  register: (userData: RegisterFormData) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  setUser: (user: User) => void;
  setToken: (token: string) => void;
  clearError: () => void;
  initializeAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (credentials: LoginFormData) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authAPI.login(credentials.email, credentials.password);
          const { access, user } = response.data;
          
          // Store token in AsyncStorage
          await AsyncStorage.setItem('auth_token', access);
          
          set({
            user,
            token: access,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          const errorMessage = error.response?.data?.message || 'Login failed';
          set({
            isLoading: false,
            error: errorMessage,
            isAuthenticated: false,
          });
          throw error;
        }
      },

      register: async (userData: RegisterFormData) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authAPI.register({
            email: userData.email,
            password: userData.password,
            first_name: userData.first_name,
            last_name: userData.last_name,
          });
          
          const { access, user } = response.data;
          
          // Store token in AsyncStorage
          await AsyncStorage.setItem('auth_token', access);
          
          set({
            user,
            token: access,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          const errorMessage = error.response?.data?.message || 'Registration failed';
          set({
            isLoading: false,
            error: errorMessage,
            isAuthenticated: false,
          });
          throw error;
        }
      },

      logout: async () => {
        try {
          await authAPI.logout();
        } catch (error) {
          console.error('Logout API error:', error);
        } finally {
          // Clear local storage
          await AsyncStorage.removeItem('auth_token');
          await AsyncStorage.removeItem('refresh_token');
          
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      },

      refreshToken: async () => {
        try {
          const refreshToken = await AsyncStorage.getItem('refresh_token');
          if (!refreshToken) {
            throw new Error('No refresh token available');
          }

          const response = await authAPI.refreshToken(refreshToken);
          const { access } = response.data;
          
          await AsyncStorage.setItem('auth_token', access);
          
          set({
            token: access,
            isAuthenticated: true,
          });
        } catch (error) {
          // If refresh fails, logout user
          await get().logout();
          throw error;
        }
      },

      setUser: (user: User) => {
        set({ user });
      },

      setToken: (token: string) => {
        set({ token, isAuthenticated: true });
      },

      clearError: () => {
        set({ error: null });
      },

      initializeAuth: async () => {
        try {
          const token = await AsyncStorage.getItem('auth_token');
          if (token) {
            set({
              token,
              isAuthenticated: true,
            });
            
            // Optionally fetch user profile here
            // const userResponse = await userAPI.getProfile();
            // set({ user: userResponse.data });
          }
        } catch (error) {
          console.error('Error initializing auth:', error);
          await get().logout();
        }
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);




