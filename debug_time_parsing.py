#!/usr/bin/env python3
"""
Debug script to test time parsing regex patterns
"""
import re

def test_time_patterns():
    """Test various time parsing patterns"""
    test_content = "remember to buy lunch and breakfast for 8:35 p.m."
    
    print("🧪 Testing Time Parsing Patterns")
    print("=" * 40)
    print(f"Test content: '{test_content}'")
    
    # Test the current patterns
    patterns = [
        r'\b(for \d{1,2}:\d{2}(?::\d{2})?(?:\s*(?:am|pm|a\.m\.|p\.m\.))?)\b',
        r'\b(\d{1,2}:\d{2}(?::\d{2})?(?:\s*(?:am|pm|a\.m\.|p\.m\.))?)\b',
        r'(?:at|for)\s+(\d{1,2}):(\d{2})(?::(\d{2}))?(?:\s*(am|pm|a\.m\.|p\.m\.))?',
        r'(\d{1,2}):(\d{2})(?::(\d{2}))?(?:\s*(am|pm|a\.m\.|p\.m\.))?'
    ]
    
    for i, pattern in enumerate(patterns):
        print(f"\nPattern {i+1}: {pattern}")
        matches = re.finditer(pattern, test_content, re.IGNORECASE)
        for match in matches:
            print(f"  Match: '{match.group()}'")
            print(f"  Groups: {match.groups()}")
            print(f"  Start/End: {match.start()}/{match.end()}")
    
    # Test a simpler approach
    print(f"\n🔍 Testing simpler approach...")
    simple_pattern = r'for\s+(\d{1,2}):(\d{2})\s*(p\.m\.)'
    match = re.search(simple_pattern, test_content, re.IGNORECASE)
    if match:
        print(f"  Simple match: '{match.group()}'")
        print(f"  Groups: {match.groups()}")
        hour = int(match.group(1))
        minute = int(match.group(2))
        ampm = match.group(3)
        print(f"  Hour: {hour}, Minute: {minute}, AM/PM: {ampm}")
        
        # Convert to 24-hour
        if ampm.lower().replace('.', '') == 'pm' and hour != 12:
            hour += 12
        print(f"  24-hour time: {hour:02d}:{minute:02d}")

if __name__ == "__main__":
    test_time_patterns()

