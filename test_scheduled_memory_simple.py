#!/usr/bin/env python3
"""
Simple test for scheduled memory functionality without UserProfile dependencies
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Add the memora_core directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from memory_assistant.models import Memory, User
from memory_assistant.smart_reminder_service import SmartReminderService
from django.utils import timezone

def test_scheduled_memory_simple():
    """Test the scheduled memory functionality without UserProfile"""
    print("🧪 Testing Scheduled Memory Functionality")
    print("=" * 50)
    
    # Get or create test user
    try:
        user = User.objects.get(username='test_user')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='testpass123'
        )
    
    print(f"✅ User: {user.username}")
    print()
    
    # Test 1: Create a scheduled memory
    print("📝 Test 1: Creating scheduled memory")
    memory_content = "remember to call my mom tomorrow at 9:00 am"
    
    # Set delivery date to tomorrow at 9:00 AM (timezone-aware)
    tomorrow = timezone.now() + timedelta(days=1)
    delivery_date = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
    
    memory = Memory.objects.create(
        user=user,
        content=memory_content,
        delivery_type='scheduled',
        delivery_date=delivery_date,
        memory_type='reminder',
        importance=8
    )
    
    print(f"✅ Memory created: ID {memory.id}")
    print(f"✅ Content: {memory.content}")
    print(f"✅ Delivery date: {memory.delivery_date}")
    print(f"✅ Delivery type: {memory.delivery_type}")
    print()
    
    # Test 2: Generate smart reminders
    print("🤖 Test 2: Generating smart reminders")
    service = SmartReminderService()
    suggestions = service.analyze_memory_for_reminders(memory)
    
    print(f"✅ Found {len(suggestions)} reminder suggestions")
    for i, suggestion in enumerate(suggestions):
        print(f"   {i+1}. {suggestion['type']} - {suggestion['description']}")
    print()
    
    # Test 3: Create smart reminders
    print("⏰ Test 3: Creating smart reminders")
    
    # Clean up any existing reminders for this memory first
    from memory_assistant.models import SmartReminder
    SmartReminder.objects.filter(memory=memory, user=user).delete()
    
    created_reminders = []
    for suggestion in suggestions:
        try:
            reminder = service.create_smart_reminder(memory, user, suggestion)
            if reminder:
                created_reminders.append(reminder)
        except Exception as e:
            print(f"   ⚠️  Failed to create reminder: {str(e)}")
            continue
    
    print(f"✅ Created {len(created_reminders)} smart reminders")
    for reminder in created_reminders:
        print(f"   - {reminder.reminder_type} reminder")
        print(f"     Next trigger: {reminder.next_trigger}")
        print(f"     Priority: {reminder.priority}")
    print()
    
    # Test 4: Check scheduled reminders endpoint
    print("🔍 Test 4: Testing scheduled reminders endpoint")
    from memory_assistant.flutter_api_views import FlutterScheduledRemindersAPIView
    from django.test import RequestFactory
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/api/v1/smart-reminders/scheduled/')
    request.user = user
    
    # Test the endpoint
    view = FlutterScheduledRemindersAPIView()
    response = view.get(request)
    
    print(f"✅ Endpoint response status: {response.status_code}")
    if response.status_code == 200:
        data = response.data
        print(f"✅ Found {data['total_count']} scheduled reminders")
        for reminder in data['scheduled_reminders']:
            print(f"   - Memory ID: {reminder['memory']}")
            print(f"     Next trigger: {reminder['next_trigger']}")
            if 'scheduled_info' in reminder:
                scheduled_info = reminder['scheduled_info']
                print(f"     Can snooze: {scheduled_info['can_snooze']}")
                print(f"     Can decline: {scheduled_info['can_decline']}")
                print(f"     Can mark done: {scheduled_info['can_mark_done']}")
    print()
    
    # Test 5: Test scheduled memory actions
    print("🎯 Test 5: Testing scheduled memory actions")
    from memory_assistant.flutter_api_views import FlutterScheduledMemoryActionsAPIView
    
    # Test snooze action
    print("   Testing snooze action...")
    snooze_request = factory.post(f'/api/v1/flutter/memories/{memory.id}/scheduled-actions/', {
        'action': 'snooze',
        'hours': 2
    })
    snooze_request.user = user
    
    action_view = FlutterScheduledMemoryActionsAPIView()
    snooze_response = action_view.post(snooze_request, memory.id)
    
    print(f"   ✅ Snooze response status: {snooze_response.status_code}")
    if snooze_response.status_code == 200:
        data = snooze_response.data
        print(f"   ✅ Message: {data['message']}")
        print(f"   ✅ New delivery date: {data['new_delivery_date']}")
        print(f"   ✅ Snooze count: {data['snooze_count']}")
    
    # Refresh memory from database
    memory.refresh_from_db()
    print(f"   ✅ Updated memory delivery date: {memory.delivery_date}")
    print()
    
    # Test 6: Test mark done action
    print("✅ Test 6: Testing mark done action")
    done_request = factory.post(f'/api/v1/flutter/memories/{memory.id}/scheduled-actions/', {
        'action': 'mark_done'
    })
    done_request.user = user
    
    done_response = action_view.post(done_request, memory.id)
    
    print(f"✅ Mark done response status: {done_response.status_code}")
    if done_response.status_code == 200:
        data = done_response.data
        print(f"✅ Message: {data['message']}")
        print(f"✅ Completed at: {data['completed_at']}")
    
    # Refresh memory from database
    memory.refresh_from_db()
    print(f"✅ Memory completed: {memory.is_completed}")
    print(f"✅ Memory delivered: {memory.is_delivered}")
    print()
    
    print("🎉 Scheduled memory functionality test completed!")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    test_scheduled_memory_simple()
