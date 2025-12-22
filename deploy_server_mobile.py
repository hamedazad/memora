#!/usr/bin/env python3
"""
Memora Server & Mobile Deployment Script
This script sets up the complete Memora ecosystem with PostgreSQL
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path

def run_command(command, shell=True, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_requirements():
    """Check if all required software is installed"""
    requirements = {
        'python': 'python --version',
        'pip': 'pip --version',
        'node': 'node --version',
        'npm': 'npm --version',
        'git': 'git --version'
    }
    
    missing = []
    for name, command in requirements.items():
        success, stdout, stderr = run_command(command)
        if success:
            print(f"✅ {name}: {stdout.strip()}")
        else:
            print(f"❌ {name}: Not installed")
            missing.append(name)
    
    return len(missing) == 0, missing

def setup_memora_server():
    """Set up the Memora Core server"""
    print("\n🖥️  Setting up Memora Core Server...")
    print("-" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ manage.py not found. Please run this script from the memora_core directory")
        return False
    
    # Install Python dependencies
    print("📦 Installing Python dependencies...")
    success, stdout, stderr = run_command("pip install -r requirements.txt")
    if not success:
        print(f"❌ Failed to install Python dependencies: {stderr}")
        return False
    print("✅ Python dependencies installed")
    
    # Install PostgreSQL adapter
    print("📦 Installing PostgreSQL adapter...")
    success, stdout, stderr = run_command("pip install psycopg2-binary")
    if success:
        print("✅ PostgreSQL adapter installed")
    else:
        print("⚠️  Warning: Could not install psycopg2-binary")
    
    # Run PostgreSQL setup
    if os.path.exists('setup_postgresql_server.py'):
        print("🗄️  Setting up PostgreSQL...")
        success, stdout, stderr = run_command("python setup_postgresql_server.py")
        if not success:
            print(f"⚠️  PostgreSQL setup had issues: {stderr}")
    
    # Collect static files
    print("📁 Collecting static files...")
    success, stdout, stderr = run_command("python manage.py collectstatic --noinput")
    if success:
        print("✅ Static files collected")
    
    print("✅ Memora Core server setup completed!")
    return True

def setup_mobile_app():
    """Set up the mobile app"""
    print("\n📱 Setting up Mobile App...")
    print("-" * 40)
    
    mobile_path = Path("C:/mobile")
    
    if not mobile_path.exists():
        print("📁 Creating mobile app directory...")
        mobile_path.mkdir(exist_ok=True)
    
    # Copy mobile configuration
    if os.path.exists('mobile_config.json'):
        shutil.copy('mobile_config.json', mobile_path / 'config.json')
        print("✅ Mobile configuration copied")
    
    # Create React Native app structure if it doesn't exist
    if not (mobile_path / 'package.json').exists():
        print("🚀 Creating React Native app...")
        success, stdout, stderr = run_command(
            "npx react-native init MemoraApp --template react-native-template-typescript",
            cwd=str(mobile_path.parent)
        )
        if success:
            print("✅ React Native app created")
        else:
            print(f"⚠️  React Native app creation had issues: {stderr}")
    
    # Create API service file for mobile
    api_service_content = '''import AsyncStorage from '@react-native-async-storage/async-storage';
import config from './config.json';

const API_BASE_URL = __DEV__ ? config.server.development.apiUrl : config.server.production.apiUrl;

class ApiService {
  private baseUrl: string;
  private authToken: string | null = null;

  constructor() {
    this.baseUrl = API_BASE_URL;
    this.loadAuthToken();
  }

  private async loadAuthToken() {
    try {
      this.authToken = await AsyncStorage.getItem(config.authentication.tokenKey);
    } catch (error) {
      console.error('Error loading auth token:', error);
    }
  }

  private async getHeaders() {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }

    return headers;
  }

  async request(endpoint: string, options: RequestInit = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = await this.getHeaders();

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...headers,
          ...options.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Authentication
  async login(username: string, password: string) {
    const response = await this.request(config.api.endpoints.auth.login, {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });

    if (response.access) {
      this.authToken = response.access;
      await AsyncStorage.setItem(config.authentication.tokenKey, response.access);
      await AsyncStorage.setItem(config.authentication.refreshTokenKey, response.refresh);
    }

    return response;
  }

  async register(userData: any) {
    return this.request(config.api.endpoints.auth.register, {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  // Memories
  async getMemories(params: any = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `${config.api.endpoints.memories.list}?${queryString}` : config.api.endpoints.memories.list;
    return this.request(endpoint);
  }

  async createMemory(memoryData: any) {
    return this.request(config.api.endpoints.memories.create, {
      method: 'POST',
      body: JSON.stringify(memoryData),
    });
  }

  async searchMemories(query: string) {
    return this.request(`${config.api.endpoints.memories.search}?q=${encodeURIComponent(query)}`);
  }

  // AI Features
  async enhanceMemory(content: string) {
    return this.request(config.api.endpoints.ai.enhance, {
      method: 'POST',
      body: JSON.stringify({ content }),
    });
  }

  async getAISuggestions() {
    return this.request(config.api.endpoints.ai.suggestions);
  }

  // Voice Features
  async transcribeVoice(audioFile: any) {
    const formData = new FormData();
    formData.append('audio', audioFile);

    return this.request(config.api.endpoints.voice.transcribe, {
      method: 'POST',
      body: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }
}

export default new ApiService();
'''
    
    api_file_path = mobile_path / 'src' / 'services' / 'ApiService.ts'
    api_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(api_file_path, 'w') as f:
        f.write(api_service_content)
    print("✅ Mobile API service created")
    
    print("✅ Mobile app setup completed!")
    return True

def create_start_scripts():
    """Create convenient start scripts"""
    
    # Server start script
    server_script = '''@echo off
echo Starting Memora Core Server...
cd /d C:\\memora_core
python manage.py runserver 0.0.0.0:8000
pause
'''
    with open('start_server.bat', 'w') as f:
        f.write(server_script)
    
    # Mobile start script
    mobile_script = '''@echo off
echo Starting Memora Mobile App...
cd /d C:\\mobile\\MemoraApp
npx react-native start
pause
'''
    with open('start_mobile.bat', 'w') as f:
        f.write(mobile_script)
    
    print("✅ Start scripts created (start_server.bat, start_mobile.bat)")

def main():
    """Main deployment function"""
    print("🚀 Memora Server & Mobile Deployment")
    print("=" * 50)
    
    # Check requirements
    print("🔍 Checking requirements...")
    requirements_ok, missing = check_requirements()
    if not requirements_ok:
        print(f"❌ Missing requirements: {', '.join(missing)}")
        print("Please install the missing software and try again.")
        return
    
    # Setup server
    if not setup_memora_server():
        print("❌ Server setup failed")
        return
    
    # Setup mobile app
    if not setup_mobile_app():
        print("❌ Mobile app setup failed")
        return
    
    # Create start scripts
    create_start_scripts()
    
    print("\n🎉 Deployment completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Configure PostgreSQL (run setup_postgresql_server.py if not done)")
    print("   2. Update .env file with your API keys")
    print("   3. Create superuser: python manage.py createsuperuser")
    print("   4. Start server: python manage.py runserver 0.0.0.0:8000")
    print("   5. Start mobile app: cd C:\\mobile\\MemoraApp && npx react-native start")
    print("\n🌐 Access points:")
    print("   • Web interface: http://localhost:8000")
    print("   • API endpoints: http://localhost:8000/api/v1/")
    print("   • Admin panel: http://localhost:8000/admin/")
    print("   • Mobile app will connect to the same server")

if __name__ == "__main__":
    main()


