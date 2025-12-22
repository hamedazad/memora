#!/usr/bin/env python3
"""
Test API endpoints to verify they're working correctly
"""

import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

def test_api_endpoints():
    """Test the API endpoints"""
    print("🧪 Testing API Endpoints...")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api/v1"
    
    # Test login for hamed user
    print("🔐 Testing login for hamed user...")
    login_data = {
        "username": "hamed",
        "password": "hamed123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/token/", json=login_data)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data['access']
            user_id = token_data.get('user_id')
            print(f"✅ Login successful! User ID: {user_id}")
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Test dashboard stats
            print("\n📊 Testing dashboard stats...")
            stats_response = requests.get(f"{base_url}/memories/dashboard_stats/", headers=headers)
            print(f"Stats Status: {stats_response.status_code}")
            
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                print(f"✅ Stats received:")
                print(f"   Total memories: {stats_data.get('total', 0)}")
                print(f"   Recent memories count: {len(stats_data.get('recent_memories', []))}")
                
                recent_memories = stats_data.get('recent_memories', [])
                if recent_memories:
                    print(f"\n📖 Recent memories:")
                    for i, memory in enumerate(recent_memories, 1):
                        print(f"   {i}. ID: {memory.get('id')}")
                        print(f"      Title: {memory.get('title', 'No title')}")
                        print(f"      Content: {memory.get('content', '')[:50]}...")
                else:
                    print("❌ No recent memories in stats response!")
            
            # Test memories endpoint
            print("\n📚 Testing memories endpoint...")
            memories_response = requests.get(f"{base_url}/memories/?page=1&limit=5", headers=headers)
            print(f"Memories Status: {memories_response.status_code}")
            
            if memories_response.status_code == 200:
                memories_data = memories_response.json()
                results = memories_data.get('results', [])
                print(f"✅ Memories received: {len(results)} memories")
                
                if results:
                    print(f"\n📖 First memory:")
                    first_memory = results[0]
                    print(f"   ID: {first_memory.get('id')}")
                    print(f"   Title: {first_memory.get('title', 'No title')}")
                    print(f"   Content: {first_memory.get('content', '')[:50]}...")
                else:
                    print("❌ No memories in response!")
            
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api_endpoints()
