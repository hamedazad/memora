#!/usr/bin/env python3
"""
Test script to verify the fix for "remember to call my mom tomorrow at 9:00 am"
"""
import re
from datetime import datetime, timedelta
from django.utils import timezone

def test_fixed_parsing():
    """Test the fixed parsing patterns"""
    test_content = "remember to call my mom tomorrow at 9:00 am"
    
    print("🧪 Testing Fixed Mom Call Memory Parsing")
    print("=" * 50)
    print(f"Test content: '{test_content}'")
    print()
    
    # Updated patterns from smart_reminder_service.py
    call_time_patterns = [
        r'call\s+(?:my\s+)?(\w+)\s+(?:at|on)\s+(\d{1,2}):?(\d{2})\s*(a\.?m\.?|p\.?m\.?)?',
        r'call\s+(?:my\s+)?(\w+)\s+(\d{1,2}):?(\d{2})\s*(a\.?m\.?|p\.?m\.?)?',
        r'(\w+)\s+call\s+(?:at|on)\s+(\d{1,2}):?(\d{2})\s*(a\.?m\.?|p\.?m\.?)?',
        # Patterns with "tomorrow"
        r'call\s+(?:my\s+)?(\w+)\s+tomorrow\s+at\s+(\d{1,2}):?(\d{2})\s*(a\.?m\.?|p\.?m\.?)?',
        r'call\s+(?:my\s+)?(\w+)\s+tomorrow\s+(\d{1,2}):?(\d{2})\s*(a\.?m\.?|p\.?m\.?)?',
        # Patterns with "tonight"
        r'call\s+(?:my\s+)?(\w+)\s+tonight\s+at\s+(\d{1,2}):?(\d{2})\s*(a\.?m\.?|p\.?m\.?)?',
        r'call\s+(?:my\s+)?(\w+)\s+tonight\s+(\d{1,2}):?(\d{2})\s*(a\.?m\.?|p\.?m\.?)?',
    ]
    
    print("🔍 Testing Updated Call Time Patterns:")
    for i, pattern in enumerate(call_time_patterns):
        print(f"\nPattern {i+1}: {pattern}")
        matches = re.finditer(pattern, test_content, re.IGNORECASE)
        for match in matches:
            print(f"  ✅ Match: '{match.group()}'")
            print(f"  Groups: {match.groups()}")
            print(f"  Start/End: {match.start()}/{match.end()}")
            
            # Test the processing logic
            try:
                person = match.group(1)
                hour = int(match.group(2))
                minute = int(match.group(3)) if match.group(3) else 0
                ampm = match.group(4).lower() if len(match.groups()) >= 4 and match.group(4) else ''
                
                # Convert to 24-hour format
                if ampm in ['pm', 'p.m.'] and hour != 12:
                    hour += 12
                elif ampm in ['am', 'a.m.'] and hour == 12:
                    hour = 0
                
                # Determine if this is a "tomorrow" or "tonight" call
                is_tomorrow = 'tomorrow' in match.group(0).lower()
                is_tonight = 'tonight' in match.group(0).lower()
                
                # Calculate target date
                now = datetime.now()
                if is_tomorrow:
                    target_date = now + timedelta(days=1)
                    target_date = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    description = f"Call {person} tomorrow at {hour:02d}:{minute:02d}"
                elif is_tonight:
                    target_date = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    if target_date <= now:
                        target_date = target_date + timedelta(days=1)
                    description = f"Call {person} tonight at {hour:02d}:{minute:02d}"
                else:
                    target_date = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    if target_date <= now:
                        target_date = target_date + timedelta(days=1)
                    description = f"Call {person} at {hour:02d}:{minute:02d}"
                
                print(f"  📅 Target DateTime: {target_date}")
                print(f"  📝 Description: {description}")
                print(f"  🎯 Is Tomorrow: {is_tomorrow}")
                print(f"  🌙 Is Tonight: {is_tonight}")
                
            except (IndexError, ValueError) as e:
                print(f"  ❌ Error processing: {e}")
    
    # Test other variations
    test_cases = [
        "call my dad tomorrow at 2:00 pm",
        "call mom tonight at 8:00 pm",
        "call john tomorrow 10:30 am",
        "meeting with team tomorrow at 3:00 pm",
    ]
    
    print(f"\n🧪 Testing Other Variations:")
    for test_case in test_cases:
        print(f"\nTest: '{test_case}'")
        for pattern in call_time_patterns:
            match = re.search(pattern, test_case, re.IGNORECASE)
            if match:
                print(f"  ✅ Matched with pattern: {pattern}")
                print(f"  Groups: {match.groups()}")
                break
        else:
            print(f"  ❌ No match found")

if __name__ == "__main__":
    test_fixed_parsing()











































