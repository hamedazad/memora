#!/usr/bin/env python
import re
from datetime import datetime, timedelta
from django.utils import timezone
from .models import SmartReminder, ReminderTrigger, Memory
from .ai_services import AIService

class SmartReminderService:
    """Enhanced service for analyzing memories and creating smart reminders with scheduled memory integration"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    def analyze_memory_for_reminders(self, memory):
        """Analyze memory content and suggest smart reminders with enhanced scheduled memory support"""
        content = memory.content.lower()
        
        # Check if this memory is about a past event
        if self._is_past_event(memory):
            return []  # Don't create reminders for past events
        
        suggestions = []
        
        # PRIORITY 1: Handle scheduled memories (with delivery_date)
        if memory.delivery_date:
            scheduled_suggestions = self._create_scheduled_memory_reminders(memory)
            suggestions.extend(scheduled_suggestions)
        
        # PRIORITY 2: Handle time-sensitive content patterns
        time_suggestions = self._detect_time_patterns(content)
        suggestions.extend(time_suggestions)
        
        # PRIORITY 3: Handle specific activity patterns
        meeting_suggestions = self._detect_meetings(content)
        suggestions.extend(meeting_suggestions)
        
        deadline_suggestions = self._detect_deadlines(content)
        suggestions.extend(deadline_suggestions)
        
        health_suggestions = self._detect_health_reminders(content)
        suggestions.extend(health_suggestions)
        
        personal_suggestions = self._detect_personal_tasks(content)
        suggestions.extend(personal_suggestions)
        
        work_suggestions = self._detect_work_tasks(content)
        suggestions.extend(work_suggestions)
        
        # Remove duplicates and prioritize scheduled memories
        unique_suggestions = self._deduplicate_suggestions(suggestions, memory)
        
        return unique_suggestions
    
    def _create_scheduled_memory_reminders(self, memory):
        """Create intelligent reminders for scheduled memories"""
        suggestions = []
        delivery_date = memory.delivery_date
        delivery_type = memory.delivery_type
        
        if not delivery_date:
            return suggestions
        
        now = timezone.now()
        
        # Calculate time until delivery
        time_until_delivery = delivery_date - now
        
        # Skip if delivery date is in the past
        if time_until_delivery.total_seconds() <= 0:
            return suggestions
        
        # Determine reminder strategy based on delivery type and importance
        if delivery_type == 'scheduled':
            suggestions.extend(self._create_scheduled_reminders(memory, delivery_date))
        elif delivery_type == 'recurring':
            suggestions.extend(self._create_recurring_reminders(memory, delivery_date))
        elif delivery_type == 'conditional':
            suggestions.extend(self._create_conditional_reminders(memory, delivery_date))
        else:  # immediate
            suggestions.extend(self._create_immediate_reminders(memory, delivery_date))
        
        return suggestions
    
    def _create_scheduled_reminders(self, memory, delivery_date):
        """Create reminders for scheduled memories"""
        suggestions = []
        importance = memory.importance
        content = memory.content.lower()
        
        # Determine advance notice based on importance and content type
        advance_notices = self._get_advance_notices_for_memory(memory, delivery_date)
        
        for advance_hours in advance_notices:
            reminder_time = delivery_date - timedelta(hours=advance_hours)
            
            # Skip if reminder time is in the past
            if reminder_time <= timezone.now():
                continue
            
            # Determine priority based on importance and advance time
            priority = self._determine_priority(importance, advance_hours)
            
            suggestions.append({
                'type': 'time_based',
                'priority': priority,
                'description': f"{memory.get_memory_type_display()} reminder: {memory.content[:50]}...",
                'trigger_conditions': {
                    'target_time': delivery_date.isoformat(),
                    'reminder_time': reminder_time.isoformat(),
                    'advance_hours': advance_hours,
                    'memory_id': memory.id,
                    'reason': f"Scheduled {memory.get_memory_type_display().lower()} memory due in {advance_hours} hours"
                }
            })
        
        return suggestions
    
    def _create_recurring_reminders(self, memory, delivery_date):
        """Create reminders for recurring memories"""
        suggestions = []
        
        # Get recurring pattern from memory
        recurring_pattern = getattr(memory, 'recurring_pattern', {})
        pattern_type = recurring_pattern.get('type', 'daily')
        
        if pattern_type == 'daily':
            # Create daily reminder
            suggestions.append({
                'type': 'frequency_based',
                'priority': 'medium',
                'description': f"Daily: {memory.content[:50]}...",
                'trigger_conditions': {
                    'frequency': 'daily',
                    'target_time': delivery_date.time().isoformat(),
                    'memory_id': memory.id,
                    'reason': f"Daily recurring {memory.get_memory_type_display().lower()} task"
                }
            })
        elif pattern_type == 'weekly':
            # Create weekly reminder
            suggestions.append({
                'type': 'frequency_based',
                'priority': 'medium',
                'description': f"Weekly: {memory.content[:50]}...",
                'trigger_conditions': {
                    'frequency': 'weekly',
                    'target_day': delivery_date.strftime('%A').lower(),
                    'target_time': delivery_date.time().isoformat(),
                    'memory_id': memory.id,
                    'reason': f"Weekly recurring {memory.get_memory_type_display().lower()} task"
                }
            })
        elif pattern_type == 'monthly':
            # Create monthly reminder
            suggestions.append({
                'type': 'frequency_based',
                'priority': 'medium',
                'description': f"Monthly: {memory.content[:50]}...",
                'trigger_conditions': {
                    'frequency': 'monthly',
                    'target_day': delivery_date.day,
                    'target_time': delivery_date.time().isoformat(),
                    'memory_id': memory.id,
                    'reason': f"Monthly recurring {memory.get_memory_type_display().lower()} task"
                }
            })
        
        return suggestions
    
    def _create_conditional_reminders(self, memory, delivery_date):
        """Create reminders for conditional memories"""
        suggestions = []
        
        # Conditional memories might have specific conditions
        conditions = getattr(memory, 'trigger_conditions', {})
        
        suggestions.append({
            'type': 'context_based',
            'priority': 'medium',
            'description': f"Conditional: {memory.content[:50]}...",
            'trigger_conditions': {
                'target_time': delivery_date.isoformat(),
                'conditions': conditions,
                'memory_id': memory.id,
                'reason': f"Conditional {memory.get_memory_type_display().lower()} memory"
            }
        })
        
        return suggestions
    
    def _create_immediate_reminders(self, memory, delivery_date):
        """Create immediate reminders for urgent memories"""
        suggestions = []
        
        # For immediate delivery, create a reminder for 5 minutes from now
        reminder_time = timezone.now() + timedelta(minutes=5)
        
        suggestions.append({
            'type': 'time_based',
            'priority': 'high',
            'description': f"Urgent: {memory.content[:50]}...",
            'trigger_conditions': {
                'target_time': delivery_date.isoformat(),
                'reminder_time': reminder_time.isoformat(),
                'memory_id': memory.id,
                'reason': f"Immediate {memory.get_memory_type_display().lower()} memory"
            }
        })
        
        return suggestions
    
    def _get_advance_notices_for_memory(self, memory, delivery_date):
        """Determine appropriate advance notice times based on memory characteristics"""
        importance = memory.importance
        memory_type = memory.memory_type
        content = memory.content.lower()
        
        # Base advance notices by importance
        if importance >= 9:  # Critical
            base_notices = [24, 12, 6, 2, 1]  # 1 day, 12 hours, 6 hours, 2 hours, 1 hour
        elif importance >= 7:  # High
            base_notices = [12, 6, 2, 1]  # 12 hours, 6 hours, 2 hours, 1 hour
        elif importance >= 5:  # Medium
            base_notices = [6, 2, 1]  # 6 hours, 2 hours, 1 hour
        else:  # Low
            base_notices = [2, 1]  # 2 hours, 1 hour
        
        # Adjust based on memory type
        if memory_type == 'work':
            # Work items might need more advance notice
            base_notices.extend([48, 24])  # Add 2 days and 1 day
        elif memory_type == 'reminder':
            # Reminders might need more frequent notifications
            base_notices.extend([30, 15])  # Add 30 minutes and 15 minutes
        
        # Adjust based on content keywords
        if any(word in content for word in ['meeting', 'appointment', 'interview']):
            base_notices.extend([60, 30])  # Add 1 hour and 30 minutes
        elif any(word in content for word in ['deadline', 'due', 'submit']):
            base_notices.extend([24, 12])  # Add 1 day and 12 hours
        elif any(word in content for word in ['call', 'phone']):
            base_notices.extend([15, 5])  # Add 15 minutes and 5 minutes
        
        # Remove duplicates and sort
        unique_notices = sorted(list(set(base_notices)), reverse=True)
        
        # Limit to reasonable number of reminders (max 5)
        return unique_notices[:5]
    
    def _determine_priority(self, importance, advance_hours):
        """Determine reminder priority based on importance and advance time"""
        if importance >= 9:
            return 'critical'
        elif importance >= 7:
            return 'high'
        elif importance >= 5:
            return 'medium'
        else:
            return 'low'
    
    def _deduplicate_suggestions(self, suggestions, memory):
        """Remove duplicate suggestions and prioritize scheduled memories"""
        unique_suggestions = []
        seen_descriptions = set()
        
        # First, add scheduled memory suggestions (highest priority)
        for suggestion in suggestions:
            if 'memory_id' in suggestion['trigger_conditions']:
                if suggestion['description'] not in seen_descriptions:
                    unique_suggestions.append(suggestion)
                    seen_descriptions.add(suggestion['description'])
        
        # Then add other suggestions
        for suggestion in suggestions:
            if 'memory_id' not in suggestion['trigger_conditions']:
                if suggestion['description'] not in seen_descriptions:
                    unique_suggestions.append(suggestion)
                    seen_descriptions.add(suggestion['description'])
        
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
    
    def create_scheduled_memory_reminder(self, memory, user):
        """Create reminder specifically for scheduled memories with delivery_date"""
        if not memory.delivery_date:
            return None
        
        # Check if reminder already exists
        existing_reminder = SmartReminder.objects.filter(
            memory=memory,
            user=user,
            reminder_type='time_based'
        ).first()
        
        if existing_reminder:
            return existing_reminder
        
        # Create enhanced reminder for scheduled memory
        delivery_date = memory.delivery_date
        now = timezone.now()
        
        # Calculate appropriate advance notice
        advance_notices = self._get_advance_notices_for_memory(memory, delivery_date)
        
        # Use the first (most important) advance notice
        if advance_notices:
            advance_hours = advance_notices[0]
            reminder_time = delivery_date - timedelta(hours=advance_hours)
            
            # Skip if reminder time is in the past
            if reminder_time <= now:
                return None
            
            # Calculate offset in minutes
            offset_minutes = int((reminder_time - now).total_seconds() / 60)
            
            # Determine priority
            priority = self._determine_priority(memory.importance, advance_hours)
            
            trigger_conditions = {
                'target_time': delivery_date.isoformat(),
                'reminder_time': reminder_time.isoformat(),
                'advance_hours': advance_hours,
                'memory_id': memory.id,
                'offset_minutes': offset_minutes,
                'reason': f"Scheduled {memory.get_memory_type_display().lower()} memory due in {advance_hours} hours"
            }
            
            reminder = SmartReminder.objects.create(
                memory=memory,
                user=user,
                reminder_type='time_based',
                priority=priority,
                trigger_conditions=trigger_conditions
            )
            
            # Calculate next trigger time
            reminder.calculate_next_trigger()
            reminder.save()
            
            return reminder
        
        return None
    
    def update_scheduled_memory_reminders(self, memory):
        """Update existing reminders when a scheduled memory is modified"""
        if not memory.delivery_date:
            return
        
        # Find existing reminders for this memory
        existing_reminders = SmartReminder.objects.filter(memory=memory)
        
        for reminder in existing_reminders:
            # Update trigger conditions based on new delivery date
            delivery_date = memory.delivery_date
            now = timezone.now()
            
            # Recalculate advance notices
            advance_notices = self._get_advance_notices_for_memory(memory, delivery_date)
            
            if advance_notices:
                advance_hours = advance_notices[0]
                reminder_time = delivery_date - timedelta(hours=advance_hours)
                
                # Update trigger conditions
                reminder.trigger_conditions.update({
                    'target_time': delivery_date.isoformat(),
                    'reminder_time': reminder_time.isoformat(),
                    'advance_hours': advance_hours,
                    'offset_minutes': int((reminder_time - now).total_seconds() / 60) if reminder_time > now else 0
                })
                
                # Update priority
                reminder.priority = self._determine_priority(memory.importance, advance_hours)
                
                # Recalculate next trigger
                reminder.calculate_next_trigger()
                reminder.save()
    
    def get_scheduled_memory_reminders(self, user):
        """Get all reminders for scheduled memories"""
        return SmartReminder.objects.filter(
            user=user,
            memory__delivery_date__isnull=False,
            is_active=True
        ).select_related('memory').order_by('next_trigger')
    
    def check_and_trigger_reminders(self, user=None):
        """Check active reminders and trigger them if needed - Optimized for performance"""
        if user:
            # Check reminders for specific user with optimized query
            active_reminders = SmartReminder.objects.filter(
                user=user, 
                is_active=True
            ).select_related('memory').prefetch_related('memory__user')
        else:
            # Check all reminders (for system-wide checks)
            active_reminders = SmartReminder.objects.filter(
                is_active=True
            ).select_related('memory').prefetch_related('memory__user')
        
        triggered_reminders = []
        
        # Batch process reminders for better performance
        reminders_to_update = []
        triggers_to_create = []
        
        for reminder in active_reminders:
            if reminder.should_trigger():
                # Prepare trigger record
                trigger = ReminderTrigger(
                    reminder=reminder,
                    trigger_reason=reminder.trigger_conditions.get('reason', 'Time-based trigger')
                )
                triggers_to_create.append(trigger)
                
                # Prepare reminder update
                reminder.last_triggered = timezone.now()
                reminder.calculate_next_trigger()
                reminders_to_update.append(reminder)
        
        # Batch create triggers
        if triggers_to_create:
            ReminderTrigger.objects.bulk_create(triggers_to_create)
        
        # Batch update reminders
        if reminders_to_update:
            SmartReminder.objects.bulk_update(
                reminders_to_update, 
                ['last_triggered', 'next_trigger']
            )
        
        # Build result list
        for i, reminder in enumerate(reminders_to_update):
            triggered_reminders.append({
                'reminder': reminder,
                'trigger': triggers_to_create[i]
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
