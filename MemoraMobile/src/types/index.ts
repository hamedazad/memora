// User Types
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  username: string;
  profile_picture?: string;
  timezone?: string;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}

// Memory Types
export interface Memory {
  id: number;
  title: string;
  content: string;
  memory_type: string;
  priority: string;
  is_completed: boolean;
  completed_at?: string;
  scheduled_date?: string;
  created_at: string;
  updated_at: string;
  user: User;
  likes_count: number;
  comments_count: number;
  is_liked: boolean;
  allow_comments: boolean;
  allow_likes: boolean;
  language?: string;
  tags?: string[];
  image?: string;
  voice_recording?: string;
}

export interface MemoryFormData {
  title: string;
  content: string;
  memory_type?: string;
  priority?: string;
  scheduled_date?: string;
  allow_comments?: boolean;
  allow_likes?: boolean;
  language?: string;
  tags?: string[];
}

// Comment Types
export interface Comment {
  id: number;
  content: string;
  created_at: string;
  user: User;
  memory: number;
}

// Reminder Types
export interface Reminder {
  id: number;
  title: string;
  description: string;
  scheduled_date: string;
  reminder_type: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  user: User;
}

export interface ReminderFormData {
  title: string;
  description: string;
  scheduled_date: string;
  reminder_type: string;
}

// Organization Types
export interface Organization {
  id: number;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
  owner: User;
  members: User[];
  members_count: number;
}

// AI Types
export interface AISuggestion {
  id: number;
  title: string;
  content: string;
  confidence: number;
  category: string;
  created_at: string;
}

export interface AICategorization {
  category: string;
  confidence: number;
  tags: string[];
}

// Navigation Types
export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
  Login: undefined;
  Register: undefined;
  Home: undefined;
  Memories: undefined;
  CreateMemory: undefined;
  MemoryDetail: { memoryId: number };
  Profile: undefined;
  Settings: undefined;
  Reminders: undefined;
  CreateReminder: undefined;
  Organizations: undefined;
  OrganizationDetail: { organizationId: number };
  Search: undefined;
};

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Form Types
export interface LoginFormData {
  email: string;
  password: string;
}

export interface RegisterFormData {
  email: string;
  password: string;
  confirm_password: string;
  first_name: string;
  last_name: string;
}

// Filter Types
export interface MemoryFilters {
  search?: string;
  memory_type?: string;
  priority?: string;
  date_from?: string;
  date_to?: string;
  is_completed?: boolean;
}

// State Types
export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface MemoryState {
  memories: Memory[];
  currentMemory: Memory | null;
  isLoading: boolean;
  error: string | null;
  filters: MemoryFilters;
  pagination: {
    page: number;
    hasMore: boolean;
  };
}

export interface ReminderState {
  reminders: Reminder[];
  isLoading: boolean;
  error: string | null;
}

export interface OrganizationState {
  organizations: Organization[];
  currentOrganization: Organization | null;
  isLoading: boolean;
  error: string | null;
}

// App State
export interface AppState {
  auth: AuthState;
  memories: MemoryState;
  reminders: ReminderState;
  organizations: OrganizationState;
}

// Utility Types
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface ApiError {
  message: string;
  status: number;
  errors?: Record<string, string[]>;
}




