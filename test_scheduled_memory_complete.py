#!/usr/bin/env python3
"""
Complete test for scheduled memory functionality with snooze/decline/done actions
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

from memory_assistant.models import Memory, User, UserProfile
from memory_assistant.smart_reminder_service import SmartReminderService
from memory_assistant.push_notification_service import push_notification_service

def test_scheduled_memory_complete_flow():
    """Test the complete scheduled memory flow"""
    print("🧪 Testing Complete Scheduled Memory Flow")
    print("=" * 60)
    
    # Get or create test user
    try:
        user = User.objects.get(username='test_user')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='testpass123'
        )
    
    # Create or get user profile
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'fcm_token': 'test_fcm_token_12345',
            'device_type': 'android',
            'push_notifications_enabled': True
        }
    )
    
    print(f"✅ User: {user.username}")
    print(f"✅ Profile created: {created}")
    print(f"✅ FCM Token: {profile.fcm_token}")
    print()
    
    # Test 1: Create a scheduled memory
    print("📝 Test 1: Creating scheduled memory")
    memory_content = "remember to call my mom tomorrow at 9:00 am"
    
    # Set delivery date to tomorrow at 9:00 AM
    tomorrow = datetime.now() + timedelta(days=1)
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
    created_reminders = service.create_smart_reminders_from_suggestions(memory, suggestions)
    
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
    from django.contrib.auth.models import AnonymousUser
    
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
    
    # Test 6: Test push notification (mock)
    print("📱 Test 6: Testing push notification system")
    try:
        # Get the first reminder
        if created_reminders:
            reminder = created_reminders[0]
            
            # Create a mock trigger
            from memory_assistant.models import ReminderTrigger
            trigger = ReminderTrigger.objects.create(
                reminder=reminder,
                trigger_reason="Test trigger for scheduled memory"
            )
            
            # Test push notification
            success = push_notification_service.send_scheduled_memory_notification(memory, reminder)
            print(f"✅ Push notification sent: {success}")
            
            if success:
                print("✅ Push notification system is working!")
            else:
                print("⚠️  Push notification failed (check FCM configuration)")
        else:
            print("⚠️  No reminders to test push notifications")
    except Exception as e:
        print(f"⚠️  Push notification test failed: {str(e)}")
    print()
    
    # Test 7: Test mark done action
    print("✅ Test 7: Testing mark done action")
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
    
    print("🎉 Complete scheduled memory flow test completed!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    test_scheduled_memory_complete_flow()











































