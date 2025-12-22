#!/usr/bin/env python
"""
Test script for Flutter API integration with smart reminders
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from django.contrib.auth.models import User
from memory_assistant.models import Memory, SmartReminder
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.test import override_settings

def test_flutter_api_integration():
    """Test Flutter API integration with smart reminders"""
    print("\n" + "="*70)
    print("Testing Flutter API Integration with Smart Reminders")
    print("="*70)
    
    # Get or create test user
    try:
        user = User.objects.get(username='hamed')
        print(f"✓ Using existing user: {user.username}")
    except User.DoesNotExist:
        print("✗ User 'hamed' not found. Creating test user...")
        user = User.objects.create_user(username='hamed', password='test123')
        print(f"✓ Created test user: {user.username}")
    
    # Create JWT token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    print(f"✓ Generated JWT token")
    
    # Create test client with authentication
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    client.format = 'json'
    
    # Set proper host for testing
    with override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1']):
        # Test 1: Create Memory with Automatic Smart Reminders
        print("\n" + "-"*50)
        print("Test 1: Create Memory with Automatic Smart Reminders")
        print("-"*50)
        
        future_time = (datetime.now() + timedelta(hours=2)).isoformat()
        
        memory_data = {
            "content": "Team meeting tomorrow at 2 PM to discuss quarterly goals and project updates",
            "memory_type": "task",
            "importance": 8,
            "delivery_date": future_time,
            "delivery_type": "scheduled",
            "tags": ["work", "meeting", "quarterly"],
            "privacy_level": "private",
            "allow_comments": True,
            "allow_likes": True
        }
        
        response = client.post('/api/v1/flutter/memories/create/', memory_data)
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Memory created successfully")
            print(f"  Memory ID: {data.get('id')}")
            print(f"  Content: {data.get('content')[:50]}...")
            print(f"  Created reminders: {data.get('reminder_count', 0)}")
            
            if data.get('created_reminders'):
                print("  Smart reminders created:")
                for i, reminder in enumerate(data['created_reminders'], 1):
                    print(f"    {i}. {reminder['type']} - {reminder['priority']} priority")
                    if reminder.get('next_trigger'):
                        print(f"       Next trigger: {reminder['next_trigger']}")
            
            memory_id = data.get('id')
        else:
            print(f"✗ Memory creation failed: {response.content}")
            return
        
        # Test 2: Get Smart Reminders
        print("\n" + "-"*50)
        print("Test 2: Get Smart Reminders")
        print("-"*50)
        
        response = client.get('/api/v1/flutter/reminders/')
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Got reminders successfully")
            print(f"  Total reminders: {data.get('total_count', 0)}")
            print(f"  Has more: {data.get('has_more', False)}")
            
            reminders = data.get('reminders', [])
            if reminders:
                print("  Recent reminders:")
                for i, reminder in enumerate(reminders[:3], 1):
                    print(f"    {i}. {reminder.get('reminder_type')} - {reminder.get('priority')}")
                    print(f"       Memory: {reminder.get('memory', {}).get('content', '')[:50]}...")
                    if reminder.get('next_trigger'):
                        print(f"       Next trigger: {reminder['next_trigger']}")
        else:
            print(f"✗ Failed to get reminders: {response.content}")
        
        # Test 3: Get Reminder Statistics
        print("\n" + "-"*50)
        print("Test 3: Get Reminder Statistics")
        print("-"*50)
        
        response = client.get('/api/v1/flutter/reminders/stats/')
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Got statistics successfully")
            print(f"  Total reminders: {data.get('total_reminders', 0)}")
            print(f"  Active reminders: {data.get('active_reminders', 0)}")
            print(f"  Upcoming (24h): {data.get('upcoming_count', 0)}")
            print(f"  Triggered today: {data.get('triggered_today', 0)}")
            
            if data.get('by_type'):
                print("  By type:")
                for type_name, count in data['by_type'].items():
                    print(f"    {type_name}: {count}")
            
            if data.get('by_priority'):
                print("  By priority:")
                for priority, count in data['by_priority'].items():
                    print(f"    {priority}: {count}")
        else:
            print(f"✗ Failed to get stats: {response.content}")
        
        # Test 4: Get Memories with Reminders
        print("\n" + "-"*50)
        print("Test 4: Get Memories with Reminders")
        print("-"*50)
        
        response = client.get('/api/v1/flutter/memories/with-reminders/')
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Got memories with reminders successfully")
            
            memories = data.get('memories', [])
            if memories:
                print(f"  Found {len(memories)} memories")
                for i, memory in enumerate(memories[:2], 1):
                    print(f"    {i}. {memory.get('content', '')[:50]}...")
                    reminder_count = memory.get('reminder_count', 0)
                    print(f"       Reminders: {reminder_count}")
                    
                    if memory.get('smart_reminders'):
                        for j, reminder in enumerate(memory['smart_reminders'][:2], 1):
                            print(f"         {j}. {reminder.get('reminder_type')} - {reminder.get('priority')}")
        else:
            print(f"✗ Failed to get memories with reminders: {response.content}")
        
        # Test 5: Check for Triggered Reminders
        print("\n" + "-"*50)
        print("Test 5: Check for Triggered Reminders")
        print("-"*50)
        
        response = client.post('/api/v1/flutter/reminders/check/', {})
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Check completed successfully")
            print(f"  Triggered count: {data.get('triggered_count', 0)}")
            print(f"  Check time: {data.get('check_time')}")
            
            reminders = data.get('reminders', [])
            if reminders:
                print("  Triggered reminders:")
                for i, reminder in enumerate(reminders, 1):
                    print(f"    {i}. {reminder.get('memory_content', '')[:50]}...")
                    print(f"       Priority: {reminder.get('priority')}")
                    print(f"       Reason: {reminder.get('trigger_reason')}")
        else:
            print(f"✗ Failed to check reminders: {response.content}")
        
        # Test 6: Test Reminder Actions (if we have reminders)
        print("\n" + "-"*50)
        print("Test 6: Test Reminder Actions")
        print("-"*50)
        
        # Get a reminder ID for testing
        response = client.get('/api/v1/flutter/reminders/')
        if response.status_code == 200:
            data = response.json()
            reminders = data.get('reminders', [])
            
            if reminders:
                reminder_id = reminders[0]['id']
                print(f"Testing actions on reminder ID: {reminder_id}")
                
                # Test snooze action
                snooze_data = {
                    "action": "snooze",
                    "hours": 2,
                    "reason": "Testing snooze functionality"
                }
                
                response = client.post(f'/api/v1/flutter/reminders/{reminder_id}/actions/', snooze_data)
                print(f"Snooze response status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✓ Snooze successful: {data.get('message')}")
                    if data.get('next_trigger'):
                        print(f"  Next trigger: {data['next_trigger']}")
                else:
                    print(f"✗ Snooze failed: {response.content}")
            else:
                print("No reminders available for action testing")
        else:
            print("Could not get reminders for action testing")
        
        # Cleanup
        print("\n" + "-"*50)
        print("Cleaning up test data...")
        if 'memory_id' in locals():
            # Clean up created memory and its reminders
            try:
                memory = Memory.objects.get(id=memory_id)
                SmartReminder.objects.filter(memory=memory).delete()
                memory.delete()
                print("✓ Test data cleaned up")
            except:
                print("⚠ Could not clean up test data")
    
    print("\n" + "="*70)
    print("Flutter API Integration Tests Complete!")
    print("="*70)
    
    # Summary
    print("\n📱 Flutter API Endpoints Summary:")
    print("  POST /api/v1/flutter/memories/create/ - Create memory with auto-reminders")
    print("  GET  /api/v1/flutter/reminders/ - Get all reminders")
    print("  GET  /api/v1/flutter/reminders/stats/ - Get reminder statistics")
    print("  GET  /api/v1/flutter/memories/with-reminders/ - Get memories with reminders")
    print("  POST /api/v1/flutter/reminders/check/ - Check for triggered reminders")
    print("  POST /api/v1/flutter/reminders/{id}/actions/ - Snooze/dismiss reminders")
    
    print("\n🔑 Key Features:")
    print("  ✓ Automatic smart reminder creation when memory is created")
    print("  ✓ JWT authentication for Flutter app")
    print("  ✓ Optimized responses for mobile consumption")
    print("  ✓ Background reminder checking")
    print("  ✓ Reminder actions (snooze, dismiss, mark done)")
    print("  ✓ Comprehensive statistics and filtering")

if __name__ == '__main__':
    test_flutter_api_integration()




