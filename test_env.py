#!/usr/bin/env python3
"""
Test Environment Variables

This script tests if the .env file is being loaded correctly.
"""

import os
from dotenv import load_dotenv

def test_environment():
    """Test if environment variables are loaded."""
    print("🧪 Testing Environment Variables")
    print("=" * 40)
    
    # Load .env file
    load_dotenv()
    
    # Check OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"✅ OpenAI API Key: {api_key[:20]}...{api_key[-10:]}")
    else:
        print("❌ OpenAI API Key not found")
    
    # Check other environment variables
    app_name = os.getenv('APP_NAME', 'Not set')
    app_version = os.getenv('APP_VERSION', 'Not set')
    
    print(f"📱 App Name: {app_name}")
    print(f"🔢 App Version: {app_version}")
    
    # Test Django settings
    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
        django.setup()
        
        from django.conf import settings
        print(f"🏗️  Django Settings loaded successfully")
        
        # Test AI service
        from memory_assistant.ai_services import get_ai_service
        ai_service = get_ai_service()
        
        if ai_service:
            print("🤖 AI Service: ✅ Available")
            
            # Test with a simple request
            test_content = "Test memory content"
            categories = ai_service.auto_categorize(test_content)
            print(f"🏷️  Test Categories: {categories}")
            
        else:
            print("🤖 AI Service: ❌ Not available")
            
    except Exception as e:
        print(f"❌ Django/AI Service Error: {e}")
    
    print("\n🎯 Environment Test Complete!")

if __name__ == "__main__":
    test_environment() 