// API Configuration for Memora Core Mobile App
export const API_CONFIG = {
  // Your Django backend server
  BASE_URL: 'http://185.231.59.157/api/v1',
  
  // API Endpoints
  ENDPOINTS: {
    // Authentication
    LOGIN: '/auth/login/',
    REGISTER: '/auth/register/',
    REFRESH_TOKEN: '/auth/refresh/',
    
    // Memories
    MEMORIES: '/memories/',
    MEMORY_DETAIL: (id: string) => `/memories/${id}/`,
    CREATE_MEMORY: '/memories/',
    UPDATE_MEMORY: (id: string) => `/memories/${id}/`,
    DELETE_MEMORY: (id: string) => `/memories/${id}/`,
    
    // AI Features
    AI_SUGGESTIONS: '/ai/suggestions/',
    AI_CATEGORIZE: '/ai/categorize/',
    
    // Voice
    VOICE_UPLOAD: '/voice/upload/',
    VOICE_TRANSCRIBE: '/voice/transcribe/',
    
    // User Profile
    PROFILE: '/profile/',
    UPDATE_PROFILE: '/profile/update/',
    
    // Sync
    SYNC: '/sync/',
    OFFLINE_SYNC: '/sync/offline/',
  },
  
  // Request timeout (30 seconds)
  TIMEOUT: 30000,
  
  // Retry configuration
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
};

// Database configuration for offline storage
export const DB_CONFIG = {
  NAME: 'memora_mobile.db',
  VERSION: '1.0',
  DISPLAY_NAME: 'Memora Mobile Database',
  SIZE: 2000000, // 2MB
};

// Cache configuration
export const CACHE_CONFIG = {
  // Memory cache TTL (Time To Live) in milliseconds
  MEMORY_TTL: 5 * 60 * 1000, // 5 minutes
  USER_TTL: 30 * 60 * 1000,  // 30 minutes
  SETTINGS_TTL: 24 * 60 * 60 * 1000, // 24 hours
  
  // Maximum cache size
  MAX_MEMORY_CACHE_SIZE: 100, // items
  MAX_DISK_CACHE_SIZE: 50 * 1024 * 1024, // 50MB
};

// App configuration
export const APP_CONFIG = {
  NAME: 'Memora',
  VERSION: '1.0.0',
  BUILD_NUMBER: '1',
  
  // Feature flags
  FEATURES: {
    OFFLINE_MODE: true,
    VOICE_RECORDING: true,
    AI_SUGGESTIONS: true,
    PUSH_NOTIFICATIONS: true,
    AUTO_SYNC: true,
  },
  
  // Sync intervals (in milliseconds)
  SYNC_INTERVALS: {
    IMMEDIATE: 0,
    QUICK: 5 * 1000,    // 5 seconds
    NORMAL: 30 * 1000,  // 30 seconds
    SLOW: 5 * 60 * 1000, // 5 minutes
    BACKGROUND: 15 * 60 * 1000, // 15 minutes
  },
};






