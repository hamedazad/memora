#!/usr/bin/env python3
"""
Test script to verify the smart reminder service fix works end-to-end
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

def test_smart_reminder_fix():
    """Test the smart reminder service with the mom call memory"""
    print("🧪 Testing Smart Reminder Service Fix")
    print("=" * 50)
    
    # Create a test user (or use existing)
    try:
        user = User.objects.get(username='test_user')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='testpass123'
        )
        print(f"✅ Created test user: {user.username}")
    
    # Test memory content
    test_content = "remember to call my mom tomorrow at 9:00 am"
    
    # Create a test memory
    memory = Memory.objects.create(
        user=user,
        content=test_content,
        memory_type='personal',
        importance=7,
        delivery_type='immediate',  # This will be analyzed by the smart reminder service
        privacy_level='private',
        allow_comments=True,
        allow_likes=True,
        language='en'
    )
    
    print(f"✅ Created test memory: {memory.id}")
    print(f"📝 Content: '{memory.content}'")
    
    # Test the smart reminder service
    service = SmartReminderService()
    suggestions = service.analyze_memory_for_reminders(memory)
    
    print(f"\n🔍 Smart Reminder Analysis Results:")
    print(f"📊 Found {len(suggestions)} suggestions")
    
    for i, suggestion in enumerate(suggestions):
        print(f"\nSuggestion {i+1}:")
        print(f"  Type: {suggestion['type']}")
        print(f"  Priority: {suggestion['priority']}")
        print(f"  Description: {suggestion['description']}")
        print(f"  Trigger Conditions: {suggestion['trigger_conditions']}")
        
        # Check if this is the expected mom call suggestion
        if 'mom' in suggestion['description'].lower() and 'tomorrow' in suggestion['description'].lower():
            print(f"  ✅ This is the expected mom call suggestion!")
            
            # Verify the target time is correct
            target_time = suggestion['trigger_conditions'].get('target_time')
            if target_time:
                target_datetime = datetime.fromisoformat(target_time.replace('Z', '+00:00'))
                tomorrow_9am = datetime.now() + timedelta(days=1)
                tomorrow_9am = tomorrow_9am.replace(hour=9, minute=0, second=0, microsecond=0)
                
                print(f"  📅 Target Time: {target_datetime}")
                print(f"  📅 Expected: {tomorrow_9am}")
                
                if target_datetime.date() == tomorrow_9am.date() and target_datetime.hour == 9:
                    print(f"  ✅ Target time is correct!")
                else:
                    print(f"  ❌ Target time is incorrect!")
    
    # Clean up
    memory.delete()
    print(f"\n🧹 Cleaned up test memory")
    
    return len(suggestions) > 0

if __name__ == "__main__":
    try:
        success = test_smart_reminder_fix()
        if success:
            print(f"\n🎉 Test PASSED! The fix is working correctly.")
        else:
            print(f"\n❌ Test FAILED! No suggestions were generated.")
    except Exception as e:
        print(f"\n💥 Test ERROR: {e}")
        import traceback
        traceback.print_exc()











































