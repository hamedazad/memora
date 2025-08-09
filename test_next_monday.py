#!/usr/bin/env python3
"""
Test script to verify 'next Monday' date parsing works correctly
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from memory_assistant.services import ChatGPTService

def test_next_monday_parsing():
    """Test that 'next Monday' gets parsed correctly"""
    print("Testing 'next Monday' date parsing...")
    
    # Create service instance
    chatgpt_service = ChatGPTService()
    
    # Test content with "next Monday"
    test_content = "remember to call Sergio's father next Monday"
    
    print(f"Testing content: '{test_content}'")
    
    # Parse date references
    delivery_date, processed_content, date_info = chatgpt_service.parse_date_references(test_content)
    
    print(f"\nResults:")
    print(f"- Delivery date: {delivery_date}")
    print(f"- Date info: {date_info}")
    print(f"- Has date reference: {date_info.get('has_date_reference', False)}")
    print(f"- Date type: {date_info.get('date_type', 'None')}")
    
    # Calculate what next Monday should be
    now = datetime.now()
    current_weekday = now.weekday()  # Monday = 0, Tuesday = 1, etc.
    monday_weekday = 0  # Monday
    
    # Days until next Monday (always next week's Monday)
    days_until_next_monday = (monday_weekday - current_weekday) % 7
    if days_until_next_monday == 0:
        days_until_next_monday = 7  # If today is Monday, next Monday is 7 days away
    else:
        days_until_next_monday += 7  # Next week's Monday
    
    expected_date = (now + timedelta(days=days_until_next_monday)).replace(hour=9, minute=0, second=0, microsecond=0)
    
    print(f"\nExpected next Monday: {expected_date}")
    print(f"Current day: {now.strftime('%A, %Y-%m-%d')}")
    print(f"Days until next Monday: {days_until_next_monday}")
    
    # Check if parsing worked
    if delivery_date:
        print(f"\n✅ SUCCESS: Date parsing worked!")
        print(f"   Parsed date matches expected: {delivery_date.date() == expected_date.date()}")
    else:
        print(f"\n❌ FAILED: No delivery date was parsed")
        
    return delivery_date, date_info

if __name__ == "__main__":
    test_next_monday_parsing()
