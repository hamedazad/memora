"""
Date Recognition Service for Memory Assistant

This module provides intelligent date extraction from natural language text.
"""

import re
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, Tuple
import calendar
from dateutil import parser
from dateutil.relativedelta import relativedelta


class DateRecognitionService:
    """Service for recognizing and extracting dates from natural language text."""
    
    def __init__(self):
        self._update_current_date()
        
        # Day of week patterns
        self.day_patterns = {
            'monday': 0, 'mon': 0,
            'tuesday': 1, 'tue': 1, 'tues': 1,
            'wednesday': 2, 'wed': 2,
            'thursday': 3, 'thu': 3, 'thurs': 3,
            'friday': 4, 'fri': 4,
            'saturday': 5, 'sat': 5,
            'sunday': 6, 'sun': 6,
        }
    
    def _update_current_date(self):
        """Update the current date to ensure accuracy"""
        self.today = date.today()
        self.now = datetime.now()
    
    def extract_date_from_text(self, text: str) -> Optional[date]:
        """
        Extract a date from natural language text.
        Returns the extracted date or None if no date is found.
        """
        if not text:
            return None
        
        # Update current date for accuracy
        self._update_current_date()
        
        text_lower = text.lower().strip()
        
        # First, try to find relative date patterns (like "in 3 days")
        extracted_date = self._extract_relative_date(text_lower)
        if extracted_date:
            return extracted_date
        
        # Then try to find time-based patterns (today, tonight, etc.)
        extracted_date = self._extract_time_based_date(text_lower)
        if extracted_date:
            return extracted_date
        
        # Then try to find day of week patterns
        extracted_date = self._extract_day_of_week(text_lower)
        if extracted_date:
            return extracted_date
        
        # Finally, try to find exact date patterns
        extracted_date = self._extract_exact_date(text_lower)
        if extracted_date:
            return extracted_date
        
        return None
    
    def _extract_exact_date(self, text: str) -> Optional[date]:
        """Extract exact dates like 'December 25th', '2024-01-15', etc."""
        try:
            # Try to parse with dateutil
            parsed_date = parser.parse(text, fuzzy=True)
            return parsed_date.date()
        except:
            pass
        
        # Look for common date formats
        date_patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
            r'(\d{1,2})-(\d{1,2})-(\d{4})',  # MM-DD-YYYY
            r'(\w+)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})',  # Month DD, YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    if len(match.groups()) == 3:
                        if pattern == r'(\d{1,2})/(\d{1,2})/(\d{4})':
                            month, day, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
                        elif pattern == r'(\d{4})-(\d{1,2})-(\d{1,2})':
                            year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                        elif pattern == r'(\d{1,2})-(\d{1,2})-(\d{4})':
                            month, day, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
                        elif pattern == r'(\w+)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})':
                            month_name, day, year = match.group(1), int(match.group(2)), int(match.group(3))
                            month = datetime.strptime(month_name, '%B').month
                        
                        return date(year, month, day)
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def _get_date_patterns(self):
        """Get date patterns with current date"""
        return {
            'today': self.today,
            'tonight': self.today,
            'this evening': self.today,
            'this morning': self.today,
            'this afternoon': self.today,
            'tomorrow': self.today + timedelta(days=1),
            'tomorrow morning': self.today + timedelta(days=1),
            'tomorrow evening': self.today + timedelta(days=1),
            'tomorrow night': self.today + timedelta(days=1),
            'yesterday': self.today - timedelta(days=1),
            'next week': self.today + timedelta(days=7),
            'next month': self.today + relativedelta(months=1),
            'next year': self.today + relativedelta(years=1),
            'this week': self.today,
            'this month': self.today,
            'this year': self.today,
            'last week': self.today - timedelta(days=7),
            'last month': self.today - relativedelta(months=1),
            'last year': self.today - relativedelta(years=1),
        }
    
    def _extract_relative_date(self, text: str) -> Optional[date]:
        """Extract relative dates like 'next week', 'in 3 days', etc."""
        # Get current date patterns
        date_patterns = self._get_date_patterns()
        
        # Check for exact matches in our patterns
        for pattern, target_date in date_patterns.items():
            if pattern in text:
                return target_date
        
        # Look for "in X days/weeks/months" patterns
        patterns = [
            (r'in (\d+) days?', lambda x: self.today + timedelta(days=int(x))),
            (r'in (\d+) weeks?', lambda x: self.today + timedelta(weeks=int(x))),
            (r'in (\d+) months?', lambda x: self.today + relativedelta(months=int(x))),
            (r'in (\d+) years?', lambda x: self.today + relativedelta(years=int(x))),
            (r'(\d+) days? from now', lambda x: self.today + timedelta(days=int(x))),
            (r'(\d+) weeks? from now', lambda x: self.today + timedelta(weeks=int(x))),
        ]
        
        for pattern, date_func in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    number = int(match.group(1))
                    return date_func(number)
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def _extract_day_of_week(self, text: str) -> Optional[date]:
        """Extract day of week references like 'next Monday', 'this Friday', etc."""
        for day_name, day_num in self.day_patterns.items():
            if day_name in text:
                # Find the next occurrence of this day
                current_day = self.today.weekday()
                days_ahead = day_num - current_day
                
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                
                # Check for "next" modifier
                if 'next' in text:
                    days_ahead += 7
                
                return self.today + timedelta(days=days_ahead)
        
        return None
    
    def _extract_time_based_date(self, text: str) -> Optional[date]:
        """Extract time-based dates like 'tonight', 'this evening', etc."""
        time_patterns = {
            'tonight': self.today,
            'this evening': self.today,
            'this night': self.today,
            'today': self.today,
            'this morning': self.today,
            'this afternoon': self.today,
        }
        
        for pattern, target_date in time_patterns.items():
            if pattern in text:
                return target_date
        
        return None
    
    def analyze_text_for_date_context(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for date context and return detailed information.
        """
        extracted_date = self.extract_date_from_text(text)
        
        if not extracted_date:
            return {
                'has_date': False,
                'date': None,
                'is_today': False,
                'is_tomorrow': False,
                'is_past': False,
                'is_future': False,
                'days_until': None,
                'date_type': None
            }
        
        days_until = (extracted_date - self.today).days
        is_today = days_until == 0
        is_tomorrow = days_until == 1
        is_past = days_until < 0
        is_future = days_until > 0
        
        # Determine date type
        if is_today:
            date_type = 'today'
        elif is_tomorrow:
            date_type = 'tomorrow'
        elif is_past:
            date_type = 'past'
        elif is_future:
            if days_until <= 7:
                date_type = 'this_week'
            elif days_until <= 30:
                date_type = 'this_month'
            else:
                date_type = 'future'
        else:
            date_type = 'unknown'
        
        return {
            'has_date': True,
            'date': extracted_date,
            'is_today': is_today,
            'is_tomorrow': is_tomorrow,
            'is_past': is_past,
            'is_future': is_future,
            'days_until': days_until,
            'date_type': date_type
        }


# Global instance for easy access
date_recognition_service = DateRecognitionService() 