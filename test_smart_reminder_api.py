#!/usr/bin/env python
"""Test script to verify smart reminder API endpoints"""

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

def test_smart_reminder_api():
    """Test smart reminder API endpoints"""
    print("\n" + "="*60)
    print("Testing Smart Reminder API")
    print("="*60)
    
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
    # Force JSON format for nested data
    client.format = 'json'
    
    # Create a test memory
    from django.utils import timezone
    future_time = timezone.now() + timedelta(hours=2)
    
    memory = Memory.objects.create(
        user=user,
        content="Team meeting to discuss quarterly goals",
        memory_type='task',
        importance=8,
        delivery_date=future_time,
        delivery_type='scheduled'
    )
    print(f"\n✓ Created test memory: {memory.content[:50]}...")
    print(f"  Delivery date: {future_time}")
    
    # Test 1: Analyze memory for reminders
    print("\n" + "-"*40)
    print("Test 1: Analyze Memory API")
    
    response = client.post('/api/v1/smart-reminders/analyze/', {
        'memory_id': memory.id
    })
    
    print(f"Response status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Analysis successful")
        print(f"  Suggestions: {len(data.get('suggestions', []))}")
        for i, suggestion in enumerate(data.get('suggestions', []), 1):
            print(f"    {i}. {suggestion.get('type')} - {suggestion.get('priority')}")
    else:
        print(f"✗ Analysis failed: {response.content}")
    
    # Test 2: Create smart reminder
    print("\n" + "-"*40)
    print("Test 2: Create Smart Reminder API")
    
    response = client.post('/api/v1/smart-reminders/', {
        'memory_id': memory.id,
        'reminder_type': 'time_based',
        'priority': 'high',
        'trigger_conditions': {
            'target_time': future_time.isoformat(),
            'offset_minutes': 30,
            'reason': 'Meeting reminder'
        }
    })
    
    print(f"Response status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"✓ Reminder created successfully")
        print(f"  ID: {data.get('id')}")
        print(f"  Type: {data.get('reminder_type')}")
        print(f"  Priority: {data.get('priority')}")
        reminder_id = data.get('id')
    else:
        print(f"✗ Creation failed: {response.content}")
        reminder_id = None
    
    # Test 3: Get user reminders
    print("\n" + "-"*40)
    print("Test 3: Get User Reminders API")
    
    response = client.get('/api/v1/smart-reminders/')
    
    print(f"Response status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        reminders = data if isinstance(data, list) else data.get('results', [])
        print(f"✓ Got {len(reminders)} reminder(s)")
        for reminder in reminders[:3]:  # Show first 3
            print(f"  - {reminder.get('reminder_type')} ({reminder.get('priority')})")
    else:
        print(f"✗ Failed to get reminders: {response.content}")
    
    # Test 4: Get stats
    print("\n" + "-"*40)
    print("Test 4: Get Stats API")
    
    response = client.get('/api/v1/smart-reminders/stats/')
    
    print(f"Response status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Got statistics")
        print(f"  Total: {data.get('total_reminders')}")
        print(f"  Active: {data.get('active_reminders')}")
        print(f"  Upcoming: {data.get('upcoming_count')}")
    else:
        print(f"✗ Failed to get stats: {response.content}")
    
    # Cleanup
    print("\n" + "-"*40)
    print("Cleaning up test data...")
    if reminder_id:
        SmartReminder.objects.filter(id=reminder_id).delete()
    memory.delete()
    print("✓ Test data cleaned up")
    
    print("\n" + "="*60)
    print("Smart Reminder API Tests Complete!")
    print("="*60)

if __name__ == '__main__':
    test_smart_reminder_api()
