#!/usr/bin/env python3
"""
Test script to debug why "remember to call my mom tomorrow at 9:00 am" 
is not being recognized as a scheduled memory
"""
import re
from datetime import datetime, timedelta
from django.utils import timezone

def test_mom_call_parsing():
    """Test parsing of the specific mom call memory"""
    test_content = "remember to call my mom tomorrow at 9:00 am"
    
    print("🧪 Testing Mom Call Memory Parsing")
    print("=" * 50)
    print(f"Test content: '{test_content}'")
    print()
    
    # Test patterns from smart_reminder_service.py
    call_time_patterns = [
        r'call\s+(?:my\s+)?(\w+)\s+(?:at|on)\s+(\d{1,2}):?(\d{2})\s*(a\.?m\.?|p\.?m\.?)?',
        r'call\s+(?:my\s+)?(\w+)\s+(\d{1,2}):?(\d{2})\s*(a\.?m\.?|p\.?m\.?)?',
        r'(\w+)\s+call\s+(?:at|on)\s+(\d{1,2}):?(\d{2})\s*(a\.?m\.?|p\.?m\.?)?',
    ]
    
    print("🔍 Testing Call Time Patterns:")
    for i, pattern in enumerate(call_time_patterns):
        print(f"\nPattern {i+1}: {pattern}")
        matches = re.finditer(pattern, test_content, re.IGNORECASE)
        for match in matches:
            print(f"  Match: '{match.group()}'")
            print(f"  Groups: {match.groups()}")
            print(f"  Start/End: {match.start()}/{match.end()}")
    
    # Test "tomorrow" detection
    print(f"\n🗓️ Testing 'tomorrow' detection:")
    tomorrow_patterns = [
        r'tomorrow',
        r'tomorrow\s+at',
        r'tomorrow\s+at\s+(\d{1,2}):(\d{2})\s*(a\.?m\.?|p\.?m\.?)?',
    ]
    
    for i, pattern in enumerate(tomorrow_patterns):
        print(f"\nTomorrow Pattern {i+1}: {pattern}")
        matches = re.finditer(pattern, test_content, re.IGNORECASE)
        for match in matches:
            print(f"  Match: '{match.group()}'")
            print(f"  Groups: {match.groups()}")
    
    # Test combined pattern
    print(f"\n🔗 Testing Combined Pattern:")
    combined_pattern = r'(?:remember\s+to\s+)?call\s+(?:my\s+)?(\w+)\s+tomorrow\s+at\s+(\d{1,2}):(\d{2})\s*(a\.?m\.?|p\.?m\.?)?'
    match = re.search(combined_pattern, test_content, re.IGNORECASE)
    if match:
        print(f"  Combined Match: '{match.group()}'")
        print(f"  Groups: {match.groups()}")
        
        person = match.group(1)
        hour = int(match.group(2))
        minute = int(match.group(3))
        ampm = match.group(4).lower() if match.group(4) else ''
        
        # Convert to 24-hour format
        if ampm in ['pm', 'p.m.'] and hour != 12:
            hour += 12
        elif ampm in ['am', 'a.m.'] and hour == 12:
            hour = 0
        
        print(f"  Parsed: Call {person} at {hour:02d}:{minute:02d}")
        
        # Calculate tomorrow's date
        tomorrow = datetime.now() + timedelta(days=1)
        target_datetime = tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
        print(f"  Target DateTime: {target_datetime}")
    else:
        print("  No combined match found")
    
    # Test the exact pattern that should work
    print(f"\n✅ Testing Exact Working Pattern:")
    exact_pattern = r'call\s+(?:my\s+)?(\w+)\s+tomorrow\s+at\s+(\d{1,2}):(\d{2})\s*(a\.?m\.?|p\.?m\.?)?'
    match = re.search(exact_pattern, test_content, re.IGNORECASE)
    if match:
        print(f"  Exact Match: '{match.group()}'")
        print(f"  Groups: {match.groups()}")
    else:
        print("  No exact match found - this is the problem!")

if __name__ == "__main__":
    test_mom_call_parsing()











































