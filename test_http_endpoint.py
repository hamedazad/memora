#!/usr/bin/env python
"""
Test the HTTP endpoint directly
"""
import requests
import json

def test_http_endpoint():
    print("🧪 Testing HTTP AI Suggestions Endpoint")
    print("=" * 50)
    
    # You'll need to get a valid JWT token first
    # For now, let's test without authentication to see the error
    
    base_url = "http://127.0.0.1:8000/api/v1"
    
    print("🔍 Testing endpoint without auth (should get 401)...")
    try:
        response = requests.get(f"{base_url}/ai/suggestions/live/")
        print(f"📊 Status: {response.status_code}")
        print(f"📊 Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🔑 Testing login to get token...")
    try:
        login_data = {
            "username": "df@df.df",  # Using the test user we found
            "password": "password"   # You might need to adjust this
        }
        
        login_response = requests.post(f"{base_url}/auth/token/", json=login_data)
        print(f"📊 Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('access')
            print(f"✅ Got access token: {access_token[:20]}...")
            
            # Now test with authentication
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
                    print(f"   {i+1}. {suggestion.get('text', suggestion)}")
            else:
                print(f"❌ AI Response: {ai_response.text}")
        else:
            print(f"❌ Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error during auth test: {e}")

if __name__ == "__main__":
    test_http_endpoint()

