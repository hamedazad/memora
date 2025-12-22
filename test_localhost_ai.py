#!/usr/bin/env python
"""
Test AI suggestions with localhost URL (same as Flutter app)
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
import requests
import json

def test_localhost_ai():
    print("🧪 Testing AI Suggestions with localhost (Flutter URL)")
    print("=" * 60)
    
    # Get the hamed user
    try:
        user = User.objects.get(username='hamed')
        print(f"👤 Found user: {user.username} (ID: {user.id})")
        
        # Reset password for testing
        password = "testpass123"
        user.set_password(password)
        user.save()
        
        # Test API with localhost (same as Flutter)
        base_url = "http://localhost:8000/api/v1"
        
        print("\n🔑 Testing login with localhost...")
        login_data = {
            "username": user.username,
            "password": password
        }
        
        login_response = requests.post(f"{base_url}/auth/token/", json=login_data)
        print(f"📊 Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('access')
            print(f"✅ Got access token: {access_token[:20]}...")
            
            # Test AI suggestions endpoint with localhost
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            print(f"\n🔍 Testing AI suggestions with localhost...")
            print(f"🔍 URL: {base_url}/ai/suggestions/live/")
            print(f"🔍 Headers: {headers}")
            
            ai_response = requests.get(f"{base_url}/ai/suggestions/live/", headers=headers)
            print(f"📊 AI Status: {ai_response.status_code}")
            print(f"📊 Response Headers: {dict(ai_response.headers)}")
            print(f"📊 Response Body: {ai_response.text}")
            
            if ai_response.status_code == 200:
                suggestions = ai_response.json()
                print(f"📊 Got {len(suggestions)} suggestions")
                
                if suggestions:
                    print("📝 AI Suggestions from localhost:")
                    for i, suggestion in enumerate(suggestions):
                        if isinstance(suggestion, dict):
                            text = suggestion.get('text', str(suggestion))
                        else:
                            text = str(suggestion)
                        print(f"   {i+1}. {text}")
                else:
                    print("⚠️ No suggestions returned")
                    
            else:
                print(f"❌ AI Response: {ai_response.text}")
        else:
            print(f"❌ Login failed: {login_response.text}")
            
    except User.DoesNotExist:
        print("❌ User 'hamed' not found")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_localhost_ai()


