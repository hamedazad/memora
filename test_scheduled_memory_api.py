#!/usr/bin/env python
"""
Test script for scheduled memory functionality in Flutter API
"""

import requests
import json
from datetime import datetime, timedelta
import os

# Configuration
BASE_URL = "http://localhost:8000/api"  # Adjust as needed
USERNAME = "testuser"  # Replace with your test user
PASSWORD = "testpass"  # Replace with your test password

def get_auth_token():
    """Get JWT token for authentication"""
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    if response.status_code == 200:
        return response.json().get('access')
    else:
        print(f"Login failed: {response.text}")
        return None

def test_create_scheduled_memory():
    """Test creating a scheduled memory"""
    token = get_auth_token()
    if not token:
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test data for scheduled memory
    future_date = (datetime.now() + timedelta(days=1)).isoformat()
    
    memory_data = {
        "content": "Doctor appointment tomorrow at 3 PM - don't forget to bring insurance card",
        "memory_type": "reminder",
        "importance": 9,
        "delivery_date": future_date,
        "delivery_type": "scheduled",
        "tags": ["health", "appointment", "doctor"],
        "privacy_level": "private",
        "allow_comments": True,
        "allow_likes": True,
        "is_time_locked": False
    }
    
    print("Creating scheduled memory...")
    print(f"Data: {json.dumps(memory_data, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/flutter/memories/create/",
        headers=headers,
        json=memory_data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        data = response.json()
        print("✅ Scheduled memory created successfully!")
        print(f"Memory ID: {data['id']}")
        print(f"Delivery Date: {data['scheduled_info']['delivery_date']}")
        print(f"Reminders Created: {data['reminder_count']}")
        return data['id']
    else:
        print("❌ Failed to create scheduled memory")
        return None

def test_create_recurring_memory():
    """Test creating a recurring memory"""
    token = get_auth_token()
    if not token:
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test data for recurring memory
    future_date = (datetime.now() + timedelta(days=1)).isoformat()
    
    memory_data = {
        "content": "Weekly team standup meeting",
        "memory_type": "reminder",
        "importance": 7,
        "delivery_date": future_date,
        "delivery_type": "scheduled",
        "tags": ["work", "meeting", "standup"],
        "privacy_level": "private",
        "allow_comments": True,
        "allow_likes": True,
        "is_time_locked": False,
        "recurring_pattern": {
            "type": "weekly",
            "interval": 1,
            "days_of_week": [1, 3, 5],  # Monday, Wednesday, Friday
            "end_date": (datetime.now() + timedelta(days=30)).isoformat()
        }
    }
    
    print("\nCreating recurring memory...")
    print(f"Data: {json.dumps(memory_data, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/flutter/memories/create/",
        headers=headers,
        json=memory_data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        data = response.json()
        print("✅ Recurring memory created successfully!")
        print(f"Memory ID: {data['id']}")
        print(f"Recurring Pattern: {data['scheduled_info']['recurring_pattern']}")
        return data['id']
    else:
        print("❌ Failed to create recurring memory")
        return None

def test_scheduled_memory_actions(memory_id):
    """Test scheduled memory actions (snooze, mark done, decline)"""
    token = get_auth_token()
    if not token:
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test snooze action
    print(f"\nTesting snooze action for memory {memory_id}...")
    snooze_data = {
        "action": "snooze",
        "hours": 2,
        "reason": "Busy with other tasks"
    }
    
    response = requests.post(
        f"{BASE_URL}/flutter/memories/{memory_id}/scheduled-actions/",
        headers=headers,
        json=snooze_data
    )
    
    print(f"Snooze Status Code: {response.status_code}")
    print(f"Snooze Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Snooze action successful!")
    else:
        print("❌ Snooze action failed")
    
    # Test mark done action
    print(f"\nTesting mark done action for memory {memory_id}...")
    mark_done_data = {
        "action": "mark_done"
    }
    
    response = requests.post(
        f"{BASE_URL}/flutter/memories/{memory_id}/scheduled-actions/",
        headers=headers,
        json=mark_done_data
    )
    
    print(f"Mark Done Status Code: {response.status_code}")
    print(f"Mark Done Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Mark done action successful!")
    else:
        print("❌ Mark done action failed")

def test_get_scheduled_memories():
    """Test getting scheduled memories"""
    token = get_auth_token()
    if not token:
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\nGetting memories with reminders...")
    
    response = requests.get(
        f"{BASE_URL}/flutter/memories/with-reminders/",
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total Memories: {data.get('total_count', 0)}")
        
        scheduled_memories = [
            memory for memory in data.get('memories', [])
            if memory.get('delivery_type') == 'scheduled'
        ]
        
        print(f"Scheduled Memories: {len(scheduled_memories)}")
        
        for memory in scheduled_memories[:3]:  # Show first 3
            print(f"\nMemory ID: {memory['id']}")
            print(f"Content: {memory['content'][:50]}...")
            print(f"Delivery Date: {memory.get('delivery_date', 'N/A')}")
            print(f"Reminders: {memory.get('reminder_count', 0)}")
        
        print("✅ Successfully retrieved scheduled memories!")
        return True
    else:
        print("❌ Failed to get scheduled memories")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Scheduled Memory API Functionality")
    print("=" * 50)
    
    # Test 1: Create scheduled memory
    memory_id = test_create_scheduled_memory()
    
    # Test 2: Create recurring memory
    recurring_memory_id = test_create_recurring_memory()
    
    # Test 3: Test scheduled memory actions
    if memory_id:
        test_scheduled_memory_actions(memory_id)
    
    # Test 4: Get scheduled memories
    test_get_scheduled_memories()
    
    print("\n" + "=" * 50)
    print("🎉 Testing completed!")

if __name__ == "__main__":
    main()



