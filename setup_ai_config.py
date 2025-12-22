#!/usr/bin/env python3
"""
AI Configuration Setup Script for Memora Core
This script helps configure the AI assistant features.
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file with AI configuration"""
    env_content = """# API Configuration
API_BASE_URL=http://localhost:8000/api/v1
API_TIMEOUT=30000

# Firebase Configuration (for push notifications)
FIREBASE_API_KEY=your_firebase_api_key_here
FIREBASE_PROJECT_ID=your_project_id_here
FIREBASE_MESSAGING_SENDER_ID=your_sender_id_here
FIREBASE_APP_ID=your_app_id_here

# OpenAI Configuration (for AI features)
# Replace with your actual OpenAI API key to enable AI features
OPENAI_API_KEY=your_openai_api_key_here

# App Configuration
APP_NAME=Memora
APP_VERSION=4.2.0-release
APP_ENVIRONMENT=development

# Sync Configuration
SYNC_INTERVAL=300000
MAX_SYNC_RETRIES=3

# Notification Configuration
NOTIFICATION_CHANNEL_ID=memora-memories
NOTIFICATION_CHANNEL_NAME=Memory Reminders
"""
    
    env_path = Path('.env')
    if env_path.exists():
        print("✅ .env file already exists")
        return True
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with default configuration")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def setup_openai_key():
    """Setup OpenAI API key"""
    print("\n🔧 OpenAI API Key Setup")
    print("=" * 50)
    print("To enable AI features, you need an OpenAI API key.")
    print("1. Go to https://platform.openai.com/api-keys")
    print("2. Create a new API key")
    print("3. Copy the key and paste it below")
    print("\nNote: Your API key will be stored in the .env file")
    
    api_key = input("\nEnter your OpenAI API key (or press Enter to skip): ").strip()
    
    if not api_key:
        print("⚠️ Skipping OpenAI setup. AI features will be disabled.")
        return False
    
    # Update .env file
    env_path = Path('.env')
    if env_path.exists():
        try:
            with open(env_path, 'r') as f:
                content = f.read()
            
            # Replace the placeholder
            updated_content = content.replace('OPENAI_API_KEY=your_openai_api_key_here', f'OPENAI_API_KEY={api_key}')
            
            with open(env_path, 'w') as f:
                f.write(updated_content)
            
            print("✅ OpenAI API key configured successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to update .env file: {e}")
            return False
    else:
        print("❌ .env file not found. Please run the script again.")
        return False

def test_ai_connection():
    """Test AI service connection"""
    print("\n🧪 Testing AI Connection")
    print("=" * 50)
    
    try:
        from memory_assistant.services import ChatGPTService
        
        ai_service = ChatGPTService()
        if ai_service.is_available():
            print("✅ AI service is available and configured correctly!")
            return True
        else:
            print("❌ AI service is not available. Check your API key configuration.")
            return False
    except Exception as e:
        print(f"❌ Error testing AI service: {e}")
        return False

def main():
    """Main setup function"""
    print("🤖 Memora Core AI Assistant Setup")
    print("=" * 50)
    
    # Create .env file
    if not create_env_file():
        return
    
    # Setup OpenAI key
    setup_openai_key()
    
    # Test connection
    test_ai_connection()
    
    print("\n🎉 Setup Complete!")
    print("=" * 50)
    print("Next steps:")
    print("1. Restart the Django server: python manage.py runserver")
    print("2. Test AI features in the mobile app")
    print("3. Check the AI dashboard at /memora/ai/dashboard/")

if __name__ == "__main__":
    main()

