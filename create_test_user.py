#!/usr/bin/env python
"""
Create a test user and test the API
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

def create_test_user_and_test():
    print("🧪 Creating Test User and Testing API")
    print("=" * 50)
    
    # Create or get test user
    username = "testuser"
    email = "test@example.com"
    password = "testpass123"
    
    try:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_active': True,
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
            print(f"✅ Created new user: {username}")
        else:
            # Update password for existing user
            user.set_password(password)
            user.save()
            print(f"✅ Updated existing user: {username}")
            
        print(f"👤 User ID: {user.id}")
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return
    
    # Test API with this user
    base_url = "http://127.0.0.1:8000/api/v1"
    
    print("\n🔑 Testing login with test user...")
    try:
        login_data = {
            "username": username,
            "password": password
        }
        
        login_response = requests.get(f"{base_url}/auth/token/", json=login_data)
        print(f"📊 Login Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            # Try POST instead of GET
            login_response = requests.post(f"{base_url}/auth/token/", json=login_data)
            print(f"📊 Login Status (POST): {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('access')
            print(f"✅ Got access token: {access_token[:20] if access_token else 'None'}...")
            
            if access_token:
                # Test AI suggestions endpoint
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                }
                
                print("\n🔍 Testing AI suggestions with auth...")
                ai_response = requests.get(f"{base_url}/ai/suggestions/live/", headers=headers)
                print(f"📊 AI Status: {ai_response.status_code}")
                
                if ai_response.status_code == 200:
                    suggestions = ai_response.json()
                    print(f"📊 Got {len(suggestions)} suggestions")
                    for i, suggestion in enumerate(suggestions[:3]):
                        print(f"   {i+1}. {suggestion.get('text', str(suggestion)[:100])}")
                else:
                    print(f"❌ AI Response: {ai_response.text}")
        else:
            print(f"❌ Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error during API test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_test_user_and_test()

