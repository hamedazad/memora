#!/usr/bin/env python3
"""
Setup AI Environment for Memora

This script sets up the OpenAI API key and tests the AI features.
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Set up the environment with OpenAI API key."""
    print("🤖 Setting up AI Environment for Memora")
    print("=" * 50)
    
    # Get API key from environment or prompt user
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  No OpenAI API key found in environment")
        print("Please set your OpenAI API key in the .env file or as an environment variable")
        api_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
        if not api_key:
            print("❌ No API key provided. AI features will not be available.")
            return False
    
    # Set environment variable
    os.environ['OPENAI_API_KEY'] = api_key
    print(f"✅ OpenAI API key set in environment")
    
    # Create .env file content
    env_content = f"""# API Configuration
API_BASE_URL=http://localhost:8000/api/v1
API_TIMEOUT=30000

# Firebase Configuration (for push notifications)
FIREBASE_API_KEY=your_firebase_api_key_here
FIREBASE_PROJECT_ID=your_project_id_here
FIREBASE_MESSAGING_SENDER_ID=your_sender_id_here
FIREBASE_APP_ID=your_firebase_app_id_here

# OpenAI Configuration (for AI features)
OPENAI_API_KEY={api_key}

# App Configuration
APP_NAME=Memora
APP_VERSION=2.0.0
APP_ENVIRONMENT=development

# Sync Configuration
SYNC_INTERVAL=300000
MAX_SYNC_RETRIES=3

# Notification Configuration
NOTIFICATION_CHANNEL_ID=memora-memories
NOTIFICATION_CHANNEL_NAME=Memory Reminders
"""
    
    # Write .env file
    env_file = Path(".env")
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ Created .env file with API key")
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False
    
    return True

def test_ai_service():
    """Test the AI service with a simple request."""
    print("\n🧪 Testing AI Service")
    print("=" * 30)
    
    try:
        # Import Django and set up
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
        django.setup()
        
        # Import AI service
        from memory_assistant.ai_services import get_ai_service
        
        # Get AI service
        ai_service = get_ai_service()
        if not ai_service:
            print("❌ AI service not available")
            return False
        
        print("✅ AI service initialized successfully")
        
        # Test with a simple memory
        test_content = "I learned about Django today. It's a powerful web framework for Python."
        
        print(f"📝 Testing with content: '{test_content}'")
        
        # Test categorization
        categories = ai_service.auto_categorize(test_content)
        print(f"🏷️  Categories: {categories}")
        
        # Test summarization
        summary = ai_service.summarize_memory(test_content)
        print(f"📋 Summary: {summary}")
        
        # Test tag generation
        tags = ai_service.generate_tags(test_content)
        print(f"🏷️  Tags: {tags}")
        
        print("✅ All AI tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ AI test failed: {e}")
        return False

def show_next_steps():
    """Show next steps for using AI features."""
    print("\n🎯 Next Steps")
    print("=" * 30)
    print("1. Start your Django server:")
    print("   python manage.py runserver")
    print()
    print("2. Visit the AI Dashboard:")
    print("   http://localhost:8000/memora/ai/dashboard/")
    print()
    print("3. Test AI Features:")
    print("   - Memory Enhancement")
    print("   - Auto-Categorization")
    print("   - Smart Tagging")
    print("   - Productivity Analysis")
    print()
    print("4. Create some memories to see AI suggestions!")
    print()
    print("🚀 Your Memora app now has AI superpowers!")

def main():
    """Main function."""
    print("🚀 Memora AI Setup")
    print("=" * 50)
    
    # Check if running in the correct directory
    if not Path("manage.py").exists():
        print("❌ Please run this script from the project root directory")
        return False
    
    # Setup environment
    if not setup_environment():
        return False
    
    # Test AI service
    if not test_ai_service():
        print("⚠️  AI service test failed, but environment is set up")
        print("   You can still try the AI features manually")
    
    # Show next steps
    show_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 