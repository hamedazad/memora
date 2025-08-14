#!/usr/bin/env python
import re
from datetime import datetime, timedelta
from django.utils import timezone
from .models import SmartReminder, ReminderTrigger
from .ai_services import AIService

class SmartReminderService:
    """Service for analyzing memories and creating smart reminders"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    def analyze_memory_for_reminders(self, memory):
        """Analyze memory content and suggest smart reminders"""
        content = memory.content.lower()
        
        # Check if this memory is about a past event
        if self._is_past_event(memory):
            return []  # Don't create reminders for past events
        
        suggestions = []
        
        # Check for meeting/appointment patterns
        meeting_suggestions = self._detect_meetings(content)
        suggestions.extend(meeting_suggestions)
        
        # Check for deadline patterns
        deadline_suggestions = self._detect_deadlines(content)
        suggestions.extend(deadline_suggestions)
        
        # Check for health/wellness patterns
        health_suggestions = self._detect_health_reminders(content)
        suggestions.extend(health_suggestions)
        
        # Check for personal tasks
        personal_suggestions = self._detect_personal_tasks(content)
        suggestions.extend(personal_suggestions)
        
        # Check for work tasks
        work_suggestions = self._detect_work_tasks(content)
        suggestions.extend(work_suggestions)
        
        # Check for general time-based patterns
        time_suggestions = self._detect_time_patterns(content)
        suggestions.extend(time_suggestions)
        
        # Remove duplicates based on time and activity
        unique_suggestions = []
        seen_times = set()
        
        for suggestion in suggestions:
            if suggestion['type'] == 'time_based':
                # Extract time from reason
                time_match = re.search(r'at (\d{2}):(\d{2})', suggestion['trigger_conditions']['reason'])
                if time_match:
                    time_key = f"{time_match.group(1)}:{time_match.group(2)}"
                    if time_key not in seen_times:
                        seen_times.add(time_key)
                        unique_suggestions.append(suggestion)
                else:
                    unique_suggestions.append(suggestion)
            else:
                unique_suggestions.append(suggestion)
        
        return unique_suggestions
    
    def _is_past_event(self, memory):
        """Check if the memory is about a past event"""
        content = memory.content.lower()
        now = timezone.now()
        
        # Check for past date indicators
        past_indicators = [
            'yesterday', 'last week', 'last month', 'last year', 'last night',
            'this morning', 'this afternoon', 'earlier today', 'today morning',
            'today afternoon', 'this evening', 'tonight'  # Only if it's already past
        ]
        
        # Check for past tense verbs
        past_tense_indicators = [
            'had', 'went', 'was', 'were', 'did', 'saw', 'met', 'called',
            'finished', 'completed', 'attended', 'visited', 'talked'
        ]
        
        # Check if content contains past indicators
        for indicator in past_indicators:
            if indicator in content:
                if indicator == 'tonight':
                    # For "tonight", check if it's already past 6 PM
                    if now.hour >= 18:  # 6 PM or later
                        return True
                elif indicator in ['this morning', 'this afternoon', 'earlier today']:
                    # For "this morning/afternoon", check if it's already past that time
                    if indicator == 'this morning' and now.hour >= 12:  # Past noon
                        return True
                    elif indicator == 'this afternoon' and now.hour >= 18:  # Past 6 PM
                        return True
                    elif indicator == 'earlier today' and now.hour >= 18:  # Past 6 PM
                        return True
                else:
                    return True
        
        # Check for past tense verbs
        for verb in past_tense_indicators:
            if f" {verb} " in content or content.startswith(verb + " "):
                return True
        
        # Check memory creation date vs current date
        # If memory was created more than 24 hours ago, check if referenced times have passed
        if memory.created_at < now - timedelta(hours=24):
            # Check if the memory content suggests it's about a past event
            if any(word in content for word in ['remember', 'recall', 'think about', 'reflect on']):
                return True
            
            # Check if the memory contains time references that have already passed
            # For example: "tomorrow" in a memory created 4 days ago means "tomorrow" from 4 days ago
            if 'tomorrow' in content:
                # If memory was created more than 2 days ago, "tomorrow" has already passed
                if memory.created_at < now - timedelta(days=2):
                    return True
            
            if 'tonight' in content:
                # If memory was created more than 1 day ago, "tonight" has already passed
                if memory.created_at < now - timedelta(days=1):
                    return True
            
            if 'this morning' in content or 'this afternoon' in content or 'earlier today' in content:
                # If memory was created more than 1 day ago, these have already passed
                if memory.created_at < now - timedelta(days=1):
                    return True
        
        return False
    
    def _get_advance_time_for_activity(self, activity):
        """Determine appropriate advance time based on activity type"""
        activity_lower = activity.lower()
        
        # Meeting-related activities (need more preparation time)
        if any(word in activity_lower for word in ['meeting', 'appointment', 'interview', 'conference', 'presentation']):
            return 30  # 30 minutes before
        
        # Health-related activities (need travel/preparation time)
        elif any(word in activity_lower for word in ['doctor', 'dentist', 'hospital', 'clinic', 'medical', 'checkup']):
            return 45  # 45 minutes before
        
        # Travel-related activities
        elif any(word in activity_lower for word in ['flight', 'train', 'bus', 'travel', 'trip', 'departure']):
            return 60  # 1 hour before
        
        # Social activities (need some preparation)
        elif any(word in activity_lower for word in ['dinner', 'lunch', 'party', 'event', 'celebration', 'date']):
            return 20  # 20 minutes before
        
        # Work-related tasks
        elif any(word in activity_lower for word in ['call', 'phone', 'discussion', 'review', 'deadline']):
            return 10  # 10 minutes before
        
        # Personal tasks
        elif any(word in activity_lower for word in ['buy', 'purchase', 'shop', 'grocery', 'errand']):
            return 15  # 15 minutes before
        
        # Default for other activities
        else:
            return 15  # 15 minutes before
    
    def _detect_meetings(self, content):
        """Detect meeting/appointment patterns"""
        suggestions = []
        
        # Patterns for meetings and calls with time
        meeting_patterns = [
            r'meeting\s+(?:with|at|on)\s+(\w+)',
            r'appointment\s+(?:with|at|on)\s+(\w+)',
            r'call\s+(?:with|to)\s+(\w+)',
            r'interview\s+(?:with|at)\s+(\w+)',
            r'conference\s+(?:with|at)\s+(\w+)',
        ]
        
        # Enhanced patterns for calls with time
        call_time_patterns = [
            r'call\s+(?:my\s+)?(\w+)\s+(?:at|on)\s+(\d{1,2}):?(\d{2})\s*(a\.?m\.?|p\.?m\.?)?',
            r'call\s+(?:my\s+)?(\w+)\s+(\d{1,2}):?(\d{2})\s*(a\.?m\.?|p\.?m\.?)?',
            r'(\w+)\s+call\s+(?:at|on)\s+(\d{1,2}):?(\d{2})\s*(a\.?m\.?|p\.?m\.?)?',
        ]
        
        # Enhanced patterns for meetings with time
        meeting_time_patterns = [
            r'have\s+a\s+meeting\s+(?:at|on)\s+(\d{1,2}):(\d{2})\s*(a\.?m\.?|p\.?m\.?)?',
            r'have\s+a\s+meeting\s+(?:with\s+)?(\w+)\s+(?:at|on)\s+(\d{1,2}):(\d{2})\s*(a\.?m\.?|p\.?m\.?)?',
            r'have\s+a\s+meeting\s+(?:with\s+)?(\w+)\s+(?:\w+\s+)?(?:at|on)\s+(\d{1,2}):(\d{2})\s*(a\.?m\.?|p\.?m\.?)?',
            r'meeting\s+(?:at|on)\s+(\d{1,2}):(\d{2})\s*(a\.?m\.?|p\.?m\.?)?',
            r'meeting\s+(?:with\s+)?(\w+)\s+(?:at|on)\s+(\d{1,2}):(\d{2})\s*(a\.?m\.?|p\.?m\.?)?',
            r'meeting\s+(?:with\s+)?(\w+)\s+(?:\w+\s+)?(?:at|on)\s+(\d{1,2}):(\d{2})\s*(a\.?m\.?|p\.?m\.?)?',
        ]
        
        # Check for call patterns with time
        for pattern in call_time_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
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
                    elif not ampm:
                        # If no AM/PM specified, check context for evening indicators
                        content_lower = content.lower()
                        if any(word in content_lower for word in ['tonight', 'evening', 'dinner', 'after work', 'afternoon']):
                            # Assume PM for evening context
                            if hour < 12:
                                hour += 12
                    
                    suggestions.append({
                        'type': 'time_based',
                        'priority': 'medium',
                        'description': f"Call {person} at {hour:02d}:{minute:02d}",
                        'trigger_conditions': {
                            'offset_minutes': 10,  # 10 minutes before for calls
                            'reason': f"Call with {person} at {hour:02d}:{minute:02d} detected"
                        }
                    })
                except (IndexError, ValueError) as e:
                    # Skip invalid matches
                    continue
        
        # Check for meeting patterns with time
        for pattern in meeting_time_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                try:
                    groups = match.groups()
                    
                    # Determine if this pattern has a person or not
                    if 'have a meeting with' in pattern or 'meeting with' in pattern:
                        # Pattern with person: have a meeting with John at 9:00 pm
                        # or: have a meeting with John tonight at 9:00 pm
                        if len(groups) >= 4:
                            person = groups[0]
                            # Find the last two groups as hour and minute
                            hour = int(groups[-3]) if len(groups) >= 4 else int(groups[1])
                            minute = int(groups[-2]) if len(groups) >= 4 else int(groups[2])
                            ampm = groups[-1].lower() if groups[-1] else ''
                        else:
                            continue
                    else:
                        # Pattern without person: have a meeting at 9:00 pm
                        if len(groups) >= 3:
                            person = "team"
                            hour = int(groups[0])
                            minute = int(groups[1])
                            ampm = groups[2].lower() if groups[2] else ''
                        else:
                            continue
                    
                    # Convert to 24-hour format
                    if ampm in ['pm', 'p.m.'] and hour != 12:
                        hour += 12
                    elif ampm in ['am', 'a.m.'] and hour == 12:
                        hour = 0
                    elif not ampm:
                        # If no AM/PM specified, check context for evening indicators
                        content_lower = content.lower()
                        if any(word in content_lower for word in ['tonight', 'evening', 'dinner', 'after work', 'afternoon']):
                            # Assume PM for evening context
                            if hour < 12:
                                hour += 12
                    
                    suggestions.append({
                        'type': 'time_based',
                        'priority': 'medium',
                        'description': f"Meeting with {person} at {hour:02d}:{minute:02d}",
                        'trigger_conditions': {
                            'offset_minutes': 30,  # 30 minutes before for meetings
                            'reason': f"Meeting with {person} at {hour:02d}:{minute:02d} detected"
                        }
                    })
                except (IndexError, ValueError) as e:
                    # Skip invalid matches
                    continue
        
        # Check for regular meeting patterns (only if no time-based meeting was detected)
        if not any('Meeting with' in s['description'] for s in suggestions):
            for pattern in meeting_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    person_name = match.group(1).lower()
                    
                    # Skip if the person name is actually a day of the week
                    day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                    if person_name in day_names:
                        continue
                    
                    # Only create meeting suggestions if there's a specific time mentioned
                    # This prevents generic "Meeting with X" suggestions without time context
                    if re.search(r'\d{1,2}:\d{2}', content):
                        # Extract the time from the content to create a proper time-based suggestion
                        time_match = re.search(r'(\d{1,2}):(\d{2})', content)
                        if time_match:
                            hour = int(time_match.group(1))
                            minute = int(time_match.group(2))
                            
                            # Check for evening context
                            content_lower = content.lower()
                            if any(word in content_lower for word in ['tonight', 'evening', 'dinner', 'after work', 'afternoon']):
                                if hour < 12:
                                    hour += 12
                            
                            suggestions.append({
                                'type': 'time_based',
                                'priority': 'medium',
                                'description': f"Meeting with {match.group(1)} at {hour:02d}:{minute:02d}",
                                'trigger_conditions': {
                                    'offset_minutes': 30,  # 30 minutes before for meetings
                                    'reason': f"Meeting with {match.group(1)} at {hour:02d}:{minute:02d} detected"
                                }
                            })
        
        return suggestions
    
    def _detect_deadlines(self, content):
        """Detect deadline patterns"""
        suggestions = []
        
        # Patterns for deadlines
        deadline_patterns = [
            r'(?:due|deadline|submit|finish)\s+(?:by|on|before)\s+(\w+)',
            r'(\w+)\s+(?:is due|deadline|needs to be done)',
            r'complete\s+(?:by|before)\s+(\w+)',
        ]
        
        for pattern in deadline_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                suggestions.append({
                    'type': 'date_based',
                    'priority': 'high',
                    'description': f"Deadline: {match.group(1)}",
                    'trigger_conditions': {
                        'target_date': self._parse_date(match.group(1)),
                        'reason': f"Deadline detected: {match.group(1)}"
                    }
                })
        
        return suggestions
    
    def _detect_health_reminders(self, content):
        """Detect health/wellness patterns"""
        suggestions = []
        
        health_keywords = [
            'medicine', 'medication', 'pill', 'take', 'dose',
            'exercise', 'workout', 'gym', 'run', 'walk',
            'doctor', 'appointment', 'checkup', 'test'
        ]
        
        for keyword in health_keywords:
            if keyword in content:
                suggestions.append({
                    'type': 'frequency_based',
                    'priority': 'high',
                    'description': f"Health reminder: {keyword}",
                    'trigger_conditions': {
                        'frequency': 'daily',
                        'reason': f"Health-related content detected: {keyword}"
                    }
                })
                break  # Only create one health reminder per memory
        
        return suggestions
    
    def _detect_personal_tasks(self, content):
        """Detect personal task patterns"""
        suggestions = []
        
        personal_keywords = [
            'call mom', 'call dad', 'family', 'birthday', 'anniversary',
            'grocery', 'shopping', 'buy', 'purchase', 'pay bill',
            'clean', 'organize', 'fix', 'repair'
        ]
        
        for keyword in personal_keywords:
            if keyword in content:
                suggestions.append({
                    'type': 'frequency_based',
                    'priority': 'medium',
                    'description': f"Personal task: {keyword}",
                    'trigger_conditions': {
                        'frequency': 'weekly',
                        'reason': f"Personal task detected: {keyword}"
                    }
                })
                break
        
        return suggestions
    
    def _detect_work_tasks(self, content):
        """Detect work task patterns"""
        suggestions = []
        
        work_keywords = [
            'report', 'presentation', 'project', 'task', 'assignment',
            'review', 'approve', 'submit', 'send', 'email',
            'meeting', 'conference', 'workshop', 'training'
        ]
        
        for keyword in work_keywords:
            if keyword in content:
                suggestions.append({
                    'type': 'frequency_based',
                    'priority': 'medium',
                    'description': f"Work task: {keyword}",
                    'trigger_conditions': {
                        'frequency': 'daily',
                        'reason': f"Work task detected: {keyword}"
                    }
                })
                break
        
        return suggestions
    
    def _detect_time_patterns(self, content):
        """Detect general time-based patterns"""
        suggestions = []
        
        # More specific patterns for time-based activities
        time_patterns = [
            r'(\w+)\s+(?:at|on|for)\s+(\d{1,2}):(\d{2})\s*(a\.?m\.?|p\.?m\.?|am|pm)?',
            r'(\w+)\s+(\d{1,2}):(\d{2})\s*(a\.?m\.?|p\.?m\.?|am|pm)?',
        ]
        
        for pattern in time_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                try:
                    activity = match.group(1).lower()
                    hour = int(match.group(2))
                    minute = int(match.group(3))
                    ampm = match.group(4).lower() if len(match.groups()) >= 4 and match.group(4) else ''
                    
                    # Skip if activity is too generic
                    if activity in ['at', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'to', 'for', 'of', 'with', 'by']:
                        continue
                    
                    # Convert to 24-hour format
                    if ampm in ['pm', 'p.m.'] and hour != 12:
                        hour += 12
                    elif ampm in ['am', 'a.m.'] and hour == 12:
                        hour = 0
                    elif not ampm:
                        # If no AM/PM specified, check context for evening indicators
                        content_lower = content.lower()
                        if any(word in content_lower for word in ['tonight', 'evening', 'dinner', 'after work', 'afternoon']):
                            # Assume PM for evening context
                            if hour < 12:
                                hour += 12
                    
                    # Create unique key to avoid duplicates
                    suggestion_key = f"{activity}_{hour:02d}_{minute:02d}"
                    
                    # Check if we already have this suggestion
                    if not any(s.get('key') == suggestion_key for s in suggestions):
                        # Determine advance time based on activity type
                        offset_minutes = self._get_advance_time_for_activity(activity)
                        
                        suggestions.append({
                            'type': 'time_based',
                            'priority': 'medium',
                            'description': f"{activity.title()} at {hour:02d}:{minute:02d}",
                            'trigger_conditions': {
                                'offset_minutes': offset_minutes,
                                'reason': f"{activity.title()} at {hour:02d}:{minute:02d} detected"
                            },
                            'key': suggestion_key
                        })
                except (IndexError, ValueError) as e:
                    # Skip invalid matches
                    continue
        
        # Remove the key from final suggestions
        for suggestion in suggestions:
            suggestion.pop('key', None)
        
        return suggestions
    
    def _parse_date(self, date_string):
        """Parse date string and return ISO format"""
        # Simple date parsing - can be enhanced with more sophisticated parsing
        try:
            # Try to parse common date formats
            if 'today' in date_string.lower():
                return timezone.now().isoformat()
            elif 'tomorrow' in date_string.lower():
                return (timezone.now() + timedelta(days=1)).isoformat()
            elif 'next week' in date_string.lower():
                return (timezone.now() + timedelta(weeks=1)).isoformat()
            elif 'next month' in date_string.lower():
                return (timezone.now() + timedelta(days=30)).isoformat()
            else:
                # For now, return current date + 1 day as fallback
                return (timezone.now() + timedelta(days=1)).isoformat()
        except:
            return (timezone.now() + timedelta(days=1)).isoformat()
    
    def create_smart_reminder(self, memory, user, suggestion):
        """Create a smart reminder based on suggestion"""
        # For time-based reminders, calculate the actual trigger time
        if suggestion['type'] == 'time_based':
            # Extract time information and date context from the memory content
            content_lower = memory.content.lower()
            reason = suggestion['trigger_conditions'].get('reason', '')
            time_match = re.search(r'at (\d{2}):(\d{2})', reason)
            
            if time_match:
                target_hour = int(time_match.group(1))
                target_minute = int(time_match.group(2))
                
                # Calculate the target time based on date context
                now = timezone.now()
                
                # Get user's timezone
                user_timezone = 'America/New_York'  # Default
                if hasattr(user, 'profile') and user.profile.user_timezone:
                    user_timezone = user.profile.user_timezone
                
                # Convert current time to user's timezone
                import pytz
                user_tz = pytz.timezone(user_timezone)
                now_local = now.astimezone(user_tz)
                
                # Create target time in user's timezone
                target_time_local = now_local.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
                
                # Convert back to UTC for storage
                target_time = target_time_local.astimezone(pytz.UTC)
                
                # Adjust target time based on date context in the memory content
                if 'tonight' in content_lower:
                    # If it's already past the target time today, set for tomorrow
                    # Compare in user's local timezone to avoid timezone confusion
                    if target_time_local <= now_local:
                        target_time = target_time + timedelta(days=1)
                elif 'tomorrow' in content_lower:
                    target_time = target_time + timedelta(days=1)
                elif 'next week' in content_lower:
                    target_time = target_time + timedelta(weeks=1)
                elif 'next month' in content_lower:
                    target_time = target_time + timedelta(days=30)
                elif 'monday' in content_lower:
                    # Calculate days until next Monday
                    days_until_monday = (0 - now.weekday()) % 7
                    if days_until_monday == 0:  # Today is Monday
                        days_until_monday = 7
                    target_time = target_time + timedelta(days=days_until_monday)
                elif 'tuesday' in content_lower:
                    days_until_tuesday = (1 - now.weekday()) % 7
                    if days_until_tuesday == 0:
                        days_until_tuesday = 7
                    target_time = target_time + timedelta(days=days_until_tuesday)
                elif 'wednesday' in content_lower:
                    days_until_wednesday = (2 - now.weekday()) % 7
                    if days_until_wednesday == 0:
                        days_until_wednesday = 7
                    target_time = target_time + timedelta(days=days_until_wednesday)
                elif 'thursday' in content_lower:
                    days_until_thursday = (3 - now.weekday()) % 7
                    if days_until_thursday == 0:
                        days_until_thursday = 7
                    target_time = target_time + timedelta(days=days_until_thursday)
                elif 'friday' in content_lower:
                    days_until_friday = (4 - now.weekday()) % 7
                    if days_until_friday == 0:
                        days_until_friday = 7
                    target_time = target_time + timedelta(days=days_until_friday)
                elif 'saturday' in content_lower:
                    days_until_saturday = (5 - now.weekday()) % 7
                    if days_until_saturday == 0:
                        days_until_saturday = 7
                    target_time = target_time + timedelta(days=days_until_saturday)
                elif 'sunday' in content_lower:
                    days_until_sunday = (6 - now.weekday()) % 7
                    if days_until_sunday == 0:
                        days_until_sunday = 7
                    target_time = target_time + timedelta(days=days_until_sunday)
                else:
                    # Default: if the time has already passed today, set it for tomorrow
                    # Compare in user's local timezone to avoid timezone confusion
                    if target_time_local <= now_local:
                        target_time = target_time + timedelta(days=1)
                
                # Get the advance time for this activity type
                advance_minutes = suggestion['trigger_conditions'].get('offset_minutes', 15)
                
                # Calculate time until target
                time_until_target = int((target_time - now).total_seconds() / 60)
                
                # If we have less than advance_minutes until the target, reduce the advance time
                if time_until_target < advance_minutes:
                    advance_minutes = max(1, time_until_target - 1)  # At least 1 minute advance
                
                # Calculate offset in minutes from now (advance_minutes before the target time)
                offset_minutes = time_until_target - advance_minutes
                
                # Don't create reminders for past times (negative offset)
                if offset_minutes <= 0:
                    # If the target time is today but we don't have enough advance time,
                    # set it for tomorrow instead
                    # Compare dates in user's local timezone
                    if target_time_local.date() == now_local.date():
                        target_time = target_time + timedelta(days=1)
                        offset_minutes = int((target_time - now).total_seconds() / 60) - advance_minutes
                        if offset_minutes <= 0:
                            return None  # Still negative, skip creating this reminder
                    else:
                        return None  # Skip creating this reminder
                
                suggestion['trigger_conditions']['offset_minutes'] = offset_minutes
        
        reminder = SmartReminder.objects.create(
            memory=memory,
            user=user,
            reminder_type=suggestion['type'],
            priority=suggestion['priority'],
            trigger_conditions=suggestion['trigger_conditions']
        )
        
        # Calculate next trigger time
        reminder.calculate_next_trigger()
        reminder.save()
        
        return reminder
    
    def check_and_trigger_reminders(self, user=None):
        """Check active reminders and trigger them if needed"""
        if user:
            # Check reminders for specific user
            active_reminders = SmartReminder.objects.filter(user=user, is_active=True)
        else:
            # Check all reminders (for system-wide checks)
            active_reminders = SmartReminder.objects.filter(is_active=True)
        
        triggered_reminders = []
        
        for reminder in active_reminders:
            if reminder.should_trigger():
                # Create trigger record
                trigger = ReminderTrigger.objects.create(
                    reminder=reminder,
                    trigger_reason=reminder.trigger_conditions.get('reason', 'Time-based trigger')
                )
                
                # Update reminder
                reminder.last_triggered = timezone.now()
                reminder.calculate_next_trigger()
                reminder.save()
                
                triggered_reminders.append({
                    'reminder': reminder,
                    'trigger': trigger
                })
        
        return triggered_reminders
    
    def get_user_reminders(self, user):
        """Get all reminders for a user"""
        return SmartReminder.objects.filter(user=user, is_active=True)
    
    def dismiss_reminder(self, reminder_id, user):
        """Dismiss a reminder"""
        try:
            reminder = SmartReminder.objects.get(id=reminder_id, user=user)
            reminder.is_active = False
            reminder.save()
            return True
        except SmartReminder.DoesNotExist:
            return False
    
    def snooze_reminder(self, reminder_id, user, hours=1):
        """Snooze a reminder for specified hours"""
        try:
            reminder = SmartReminder.objects.get(id=reminder_id, user=user)
            reminder.next_trigger = timezone.now() + timedelta(hours=hours)
            reminder.save()
            return True
        except SmartReminder.DoesNotExist:
            return False
