import AsyncStorage from '@react-native-async-storage/async-storage';
import { Memory, User } from './api';

// Simple database service using AsyncStorage for Expo compatibility
class DatabaseService {
  private readonly USERS_KEY = 'users';
  private readonly MEMORIES_KEY = 'memories';
  private readonly CACHE_KEY = 'cache';

  // Initialize database (no-op for AsyncStorage)
  async initDatabase(): Promise<void> {
    try {
      console.log('AsyncStorage database initialized successfully');
    } catch (error) {
      console.error('Error initializing database:', error);
      throw error;
    }
  }

  // User operations
  async saveUser(user: User): Promise<void> {
    try {
      const users = await this.getUsers();
      const existingUserIndex = users.findIndex(u => u.id === user.id);
      
      if (existingUserIndex >= 0) {
        users[existingUserIndex] = { ...users[existingUserIndex], ...user };
      } else {
        users.push(user);
      }
      
      await AsyncStorage.setItem(this.USERS_KEY, JSON.stringify(users));
    } catch (error) {
      console.error('Error saving user:', error);
      throw error;
    }
  }

  async getUser(id: string): Promise<User | null> {
    try {
      const users = await this.getUsers();
      return users.find(user => user.id === id) || null;
    } catch (error) {
      console.error('Error getting user:', error);
      return null;
    }
  }

  private async getUsers(): Promise<User[]> {
    try {
      const usersData = await AsyncStorage.getItem(this.USERS_KEY);
      return usersData ? JSON.parse(usersData) : [];
    } catch (error) {
      console.error('Error getting users:', error);
      return [];
    }
  }

  // Memory operations
  async saveMemory(memory: Memory): Promise<void> {
    try {
      const memories = await this.getMemories();
      const existingMemoryIndex = memories.findIndex(m => m.id === memory.id);
      
      if (existingMemoryIndex >= 0) {
        memories[existingMemoryIndex] = { ...memories[existingMemoryIndex], ...memory };
      } else {
        memories.push(memory);
      }
      
      await AsyncStorage.setItem(this.MEMORIES_KEY, JSON.stringify(memories));
    } catch (error) {
      console.error('Error saving memory:', error);
      throw error;
    }
  }

  async getMemories(): Promise<Memory[]> {
    try {
      const memoriesData = await AsyncStorage.getItem(this.MEMORIES_KEY);
      return memoriesData ? JSON.parse(memoriesData) : [];
    } catch (error) {
      console.error('Error getting memories:', error);
      return [];
    }
  }

  async getMemory(id: string): Promise<Memory | null> {
    try {
      const memories = await this.getMemories();
      return memories.find(memory => memory.id === id) || null;
    } catch (error) {
      console.error('Error getting memory:', error);
      return null;
    }
  }

  async deleteMemory(id: string): Promise<void> {
    try {
      const memories = await this.getMemories();
      const filteredMemories = memories.filter(memory => memory.id !== id);
      await AsyncStorage.setItem(this.MEMORIES_KEY, JSON.stringify(filteredMemories));
    } catch (error) {
      console.error('Error deleting memory:', error);
      throw error;
    }
  }

  // Cache operations
  async setCache(key: string, value: any, ttl: number): Promise<void> {
    try {
      const cacheData = await this.getCacheData();
      const expiryTime = Date.now() + ttl;
      
      cacheData[key] = {
        value,
        ttl: expiryTime
      };
      
      await AsyncStorage.setItem(this.CACHE_KEY, JSON.stringify(cacheData));
    } catch (error) {
      console.error('Error setting cache:', error);
    }
  }

  async getCache(key: string): Promise<any | null> {
    try {
      const cacheData = await this.getCacheData();
      const cacheItem = cacheData[key];
      
      if (cacheItem && cacheItem.ttl > Date.now()) {
        return cacheItem.value;
      }
      
      // Remove expired cache
      if (cacheItem) {
        delete cacheData[key];
        await AsyncStorage.setItem(this.CACHE_KEY, JSON.stringify(cacheData));
      }
      
      return null;
    } catch (error) {
      console.error('Error getting cache:', error);
      return null;
    }
  }

  private async getCacheData(): Promise<Record<string, { value: any; ttl: number }>> {
    try {
      const cacheData = await AsyncStorage.getItem(this.CACHE_KEY);
      return cacheData ? JSON.parse(cacheData) : {};
    } catch (error) {
      console.error('Error getting cache data:', error);
      return {};
    }
  }

  async clearExpiredCache(): Promise<void> {
    try {
      const cacheData = await this.getCacheData();
      const now = Date.now();
      const validCache: Record<string, { value: any; ttl: number }> = {};
      
      for (const [key, item] of Object.entries(cacheData)) {
        if (item.ttl > now) {
          validCache[key] = item;
        }
      }
      
      await AsyncStorage.setItem(this.CACHE_KEY, JSON.stringify(validCache));
    } catch (error) {
      console.error('Error clearing expired cache:', error);
    }
  }

  // Utility methods
  async clearAllData(): Promise<void> {
    try {
      await AsyncStorage.multiRemove([this.USERS_KEY, this.MEMORIES_KEY, this.CACHE_KEY]);
    } catch (error) {
      console.error('Error clearing all data:', error);
    }
  }

  async getDatabaseSize(): Promise<number> {
    try {
      const allKeys = await AsyncStorage.getAllKeys();
      const allData = await AsyncStorage.multiGet(allKeys);
      return allData.reduce((size, [key, value]) => size + (value?.length || 0), 0);
    } catch (error) {
      console.error('Error getting database size:', error);
      return 0;
    }
  }

  // Close database (no-op for AsyncStorage)
  async closeDatabase(): Promise<void> {
    // AsyncStorage doesn't need explicit closing
  }
}

// Export singleton instance
export const databaseService = new DatabaseService();
export default databaseService;






