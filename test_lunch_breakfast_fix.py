#!/usr/bin/env python3
"""
Test script to verify the fix for lunch and breakfast reminder issue
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from memory_assistant.models import Memory, SmartReminder
from memory_assistant.services import ChatGPTService
from memory_assistant.smart_reminder_service import SmartReminderService

def test_lunch_breakfast_fix():
    """Test the fix for lunch and breakfast reminder parsing"""
    print("🧪 Testing Lunch and Breakfast Reminder Fix")
    print("=" * 50)
    
    # Get first user
    user = User.objects.first()
    if not user:
        print("❌ No users found")
        return
    
    print(f"Testing with user: {user.username}")
    
    # Test content with "for" time pattern
    test_content = "remember to buy lunch and breakfast for 8:35 p.m."
    
    print(f"\n📝 Testing content: '{test_content}'")
    
    # Test date parsing
    chatgpt_service = ChatGPTService()
    delivery_date, cleaned_content, date_info = chatgpt_service.parse_date_references(test_content)
    
    print(f"\n📅 Date Parsing Results:")
    print(f"   Delivery Date: {delivery_date}")
    print(f"   Date Info: {date_info}")
    print(f"   Has Date Reference: {date_info.get('has_date_reference', False)}")
    print(f"   Date Type: {date_info.get('date_type', 'None')}")
    
    # Test AI processing
    processed_data = chatgpt_service.process_memory(test_content)
    
    print(f"\n🤖 AI Processing Results:")
    print(f"   Summary: {processed_data.get('summary', '')}")
    print(f"   Memory Type: {processed_data.get('memory_type', 'general')}")
    print(f"   Importance: {processed_data.get('importance', 5)}")
    print(f"   Tags: {processed_data.get('tags', [])}")
    print(f"   Delivery Date: {processed_data.get('delivery_date')}")
    print(f"   Delivery Type: {processed_data.get('delivery_type', 'scheduled')}")
    
    # Create memory with the processed data
    memory = Memory.objects.create(
        user=user,
        content=test_content,
        summary=processed_data.get('summary', ''),
        ai_reasoning=processed_data.get('reasoning', ''),
        tags=processed_data.get('tags', []),
        memory_type=processed_data.get('memory_type', 'general'),
        importance=processed_data.get('importance', 5),
        delivery_type=processed_data.get('delivery_type', 'scheduled')
    )
    
    # Apply delivery date if available
    delivery_date = processed_data.get('delivery_date')
    if delivery_date and delivery_date != "None" and delivery_date is not None:
        if isinstance(delivery_date, str):
            try:
                memory.delivery_date = datetime.fromisoformat(delivery_date.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                pass
        else:
            memory.delivery_date = delivery_date
        memory.save()
    
    print(f"\n✅ Created memory ID {memory.id}")
    print(f"   Final Delivery Date: {memory.delivery_date}")
    
    # Test smart reminder creation
    reminder_service = SmartReminderService()
    suggestions = reminder_service.analyze_memory_for_reminders(memory)
    
    print(f"\n🔔 Smart Reminder Suggestions: {len(suggestions)}")
    for suggestion in suggestions:
        print(f"   - {suggestion['description']}")
        print(f"     Type: {suggestion['type']}")
        print(f"     Priority: {suggestion['priority']}")
        print(f"     Conditions: {suggestion['trigger_conditions']}")
        
        # Create the reminder
        reminder = reminder_service.create_smart_reminder(memory, user, suggestion)
        if reminder:
            print(f"     ✅ Created reminder ID {reminder.id}")
            print(f"       Next trigger: {reminder.next_trigger}")
            print(f"       Should trigger now: {reminder.should_trigger()}")
        else:
            print(f"     ❌ Failed to create reminder")
    
    # Check if the reminder should trigger
    print(f"\n🔍 Checking if reminder should trigger...")
    now = timezone.now()
    if memory.delivery_date:
        time_diff = memory.delivery_date - now
        print(f"   Time until delivery: {time_diff}")
        print(f"   Is delivery time in the future: {memory.delivery_date > now}")
    
    # Check all reminders for this memory
    reminders = SmartReminder.objects.filter(memory=memory)
    print(f"\n📋 All reminders for this memory: {reminders.count()}")
    for reminder in reminders:
        print(f"   🔔 Reminder ID {reminder.id}:")
        print(f"     Type: {reminder.reminder_type}")
        print(f"     Active: {reminder.is_active}")
        print(f"     Next Trigger: {reminder.next_trigger}")
        print(f"     Should Trigger: {reminder.should_trigger()}")

if __name__ == "__main__":
    test_lunch_breakfast_fix()

