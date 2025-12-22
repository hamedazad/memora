#!/usr/bin/env python
"""
Test the API endpoint directly
"""
import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append('C:\\memora_core')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from memory_assistant.api_views import AIViewSet

def test_api_endpoint():
    print("🧪 Testing AI API Endpoint")
    print("=" * 50)
    
    # Get a test user
    user = User.objects.first()
    if not user:
        print("❌ No users found in database")
        return
    
    print(f"👤 Testing with user: {user.username} (ID: {user.id})")
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/api/v1/ai/suggestions/live/')
    request.user = user
    
    # Test the live_suggestions endpoint
    print("\n🔍 Testing live_suggestions endpoint...")
    
    try:
        ai_viewset = AIViewSet()
        response = ai_viewset.live_suggestions(request)
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📊 Response headers: {dict(response.items())}")
        print(f"📊 Response data type: {type(response.data)}")
        print(f"📊 Response data length: {len(response.data) if isinstance(response.data, list) else 'N/A'}")
        
        if isinstance(response.data, list) and response.data:
            print("📝 Sample suggestions:")
            for i, suggestion in enumerate(response.data[:3]):
                print(f"   {i+1}. {suggestion}")
        else:
            print("⚠️ No suggestions returned")
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_endpoint()

