#!/usr/bin/env python3
"""
Test script to verify AI endpoints are working correctly
"""

import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

def test_ai_endpoints():
    """Test the AI endpoints directly"""
    print("🧪 Testing AI Endpoints...")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api/v1"
    
    # First, get a token
    print("🔐 Getting authentication token...")
    login_data = {
        "username": "hamed",  # Use the username from your login
        "password": "hamed123"  # Use the password from your login
    }
    
    try:
        response = requests.post(f"{base_url}/auth/token/", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data['access']
            user_id = token_data.get('user_id')
            print(f"✅ Token obtained, User ID: {user_id}")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test AI categorize endpoint
    print("\n🤖 Testing AI Categorize Endpoint...")
    categorize_data = {"content": "I need to prepare for the quarterly meeting tomorrow at 2 PM"}
    try:
        response = requests.post(f"{base_url}/ai/categorize", json=categorize_data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 200:
            print("✅ Categorize endpoint working!")
        else:
            print("❌ Categorize endpoint failed!")
    except Exception as e:
        print(f"❌ Categorize error: {e}")
    
    # Test AI summarize endpoint
    print("\n📝 Testing AI Summarize Endpoint...")
    summarize_data = {
        "content": "This is a long memory about my work project. I need to complete the quarterly report by Friday. The report should include sales data, customer feedback, and market analysis.",
        "max_length": 100
    }
    try:
        response = requests.post(f"{base_url}/ai/summarize", json=summarize_data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 200:
            print("✅ Summarize endpoint working!")
        else:
            print("❌ Summarize endpoint failed!")
    except Exception as e:
        print(f"❌ Summarize error: {e}")
    
    # Test AI tags endpoint
    print("\n🏷️ Testing AI Tags Endpoint...")
    tags_data = {"content": "I need to prepare for the quarterly meeting tomorrow at 2 PM"}
    try:
        response = requests.post(f"{base_url}/ai/tags", json=tags_data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 200:
            print("✅ Tags endpoint working!")
        else:
            print("❌ Tags endpoint failed!")
    except Exception as e:
        print(f"❌ Tags error: {e}")
    
    return True

if __name__ == "__main__":
    test_ai_endpoints()

