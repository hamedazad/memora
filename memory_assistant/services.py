import os
import json
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI
from django.conf import settings
from dotenv import load_dotenv
from datetime import datetime, timedelta
from django.utils import timezone
import re
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

load_dotenv()

class ChatGPTService:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and api_key != 'your_openai_api_key_here':
            try:
                self.client = OpenAI(api_key=api_key)
                self.model = "gpt-3.5-turbo"
                self._available = True
            except Exception:
                self._available = False
        else:
            self._available = False
    
    def is_available(self) -> bool:
        """Check if OpenAI API is available"""
        return self._available
    
    def parse_date_references(self, content: str) -> Tuple[Optional[datetime], str, Dict[str, Any]]:
        """
        Parse date references from memory content and extract delivery information
        
        Returns:
            Tuple of (delivery_date, cleaned_content, date_info)
        """
        if not self.is_available():
            return None, content, {}
        
        def normalize_text(text):
            """Normalize text for better matching"""
            return text.lower().strip()
        
        def fuzzy_match_tomorrow(text):
            """Fuzzy match for tomorrow variations"""
            text_lower = text.lower()
            tomorrow_variations = [
                'tomorrow', 'tommorow', 'tomorow', 'tmr', 'tmrw', 'tmrw', 'tomorow',
                'tommorrow', 'tomorow', 'tommorow', 'tomorow'
            ]
            for variation in tomorrow_variations:
                if variation in text_lower:
                    return True, variation
            return False, None
        
        # Common date patterns and their meanings (including common misspellings)
        date_patterns = {
            r'\b(today|tonight)\b': 'today',
            r'\b(tomorrow|tommorow|tmr|tmrw|tomorow)\b': 'tomorrow',  # Added common misspellings
            r'\b(yesterday)\b': 'yesterday',
            r'\b(next week|following week)\b': 'next_week',
            r'\b(this week)\b': 'this_week',
            r'\b(next month)\b': 'next_month',
            r'\b(this month)\b': 'this_month',
            r'\b(next year)\b': 'next_year',
            r'\b(this year)\b': 'this_year',
            r'\b(in \d+ days?)\b': 'days_ahead',
            r'\b(in \d+ weeks?)\b': 'weeks_ahead',
            r'\b(in \d+ months?)\b': 'months_ahead',
            r'\b(next (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun))\b': 'next_day_of_week',
            r'\b(on \w+)\b': 'day_of_week',
            r'\b(at \d{1,2}:\d{2}(?::\d{2})?(?:\s*(?:am|pm|a\.m\.|p\.m\.))?)\b': 'time',
            r'\b(for \d{1,2}:\d{2}(?::\d{2})?(?:\s*(?:am|pm|a\.m\.|p\.m\.))?)\b': 'time',
            r'\b(\d{1,2}:\d{2}(?::\d{2})?(?:\s*(?:am|pm|a\.m\.|p\.m\.))?)\b': 'time',
            # Additional patterns without word boundaries to catch AM/PM
            r'\b(at \d{1,2}:\d{2}(?::\d{2})?)\s+(?:am|pm|a\.m\.|p\.m\.)': 'time',
            r'\b(for \d{1,2}:\d{2}(?::\d{2})?)\s+(?:am|pm|a\.m\.|p\.m\.)': 'time',
            r'\b(\d{1,2}:\d{2}(?::\d{2})?)\s+(?:am|pm|a\.m\.|p\.m\.)': 'time',
        }
        
        # Time patterns
        time_patterns = {
            r'\b(morning|am)\b': 'morning',
            r'\b(afternoon|pm)\b': 'afternoon',
            r'\b(evening|night)\b': 'evening',
            r'\b(noon|midday)\b': 'noon',
            r'\b(midnight)\b': 'midnight',
        }
        
        content_lower = content.lower()
        delivery_date = None
        date_info = {
            'has_date_reference': False,
            'date_type': None,
            'time_reference': None,
            'is_recurring': False,
            'original_text': []
        }
        
        # First, try fuzzy matching for common misspellings
        is_tomorrow, tomorrow_variant = fuzzy_match_tomorrow(content)
        if is_tomorrow:
            print(f"DEBUG: Fuzzy matched tomorrow variant: '{tomorrow_variant}'")
            date_info['has_date_reference'] = True
            date_info['date_type'] = 'tomorrow'
            date_info['original_text'].append(tomorrow_variant)
            
            # Calculate tomorrow's date
            from django.utils import timezone
            now = timezone.now()
            delivery_date = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
            print(f"DEBUG: Set delivery date to: {delivery_date}")
            return delivery_date, content, date_info
        
        # Check for recurring patterns
        recurring_patterns = [
            r'\b(every day|daily)\b',
            r'\b(every week|weekly)\b',
            r'\b(every month|monthly)\b',
            r'\b(every year|yearly|annually)\b',
            r'\b(every \w+)\b'
        ]
        
        for pattern in recurring_patterns:
            if re.search(pattern, content_lower):
                date_info['is_recurring'] = True
                date_info['date_type'] = 'recurring'
                break
        
        # If it's recurring, don't set a specific delivery date
        if date_info['is_recurring']:
            return None, content, date_info
        
        # Parse specific date references
        for pattern, date_type in date_patterns.items():
            matches = re.finditer(pattern, content_lower, re.IGNORECASE)
            for match in matches:
                print(f"DEBUG: Found date pattern '{pattern}' matched '{match.group()}' for type '{date_type}'")
                date_info['has_date_reference'] = True
                date_info['date_type'] = date_type
                date_info['original_text'].append(match.group())
                
                # Calculate the actual date
                from django.utils import timezone
                now = timezone.now()
                
                if date_type == 'today':
                    delivery_date = now.replace(hour=9, minute=0, second=0, microsecond=0)  # Default to 9 AM
                elif date_type == 'tomorrow':
                    delivery_date = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
                elif date_type == 'yesterday':
                    delivery_date = (now - timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
                elif date_type == 'next_week':
                    delivery_date = (now + timedelta(weeks=1)).replace(hour=9, minute=0, second=0, microsecond=0)
                elif date_type == 'this_week':
                    # Find next occurrence of the same day of week
                    days_ahead = (7 - now.weekday()) % 7
                    if days_ahead == 0:
                        days_ahead = 7
                    delivery_date = (now + timedelta(days=days_ahead)).replace(hour=9, minute=0, second=0, microsecond=0)
                elif date_type == 'next_month':
                    delivery_date = (now + relativedelta(months=1)).replace(hour=9, minute=0, second=0, microsecond=0)
                elif date_type == 'this_month':
                    delivery_date = now.replace(day=15, hour=9, minute=0, second=0, microsecond=0)  # Mid-month
                elif date_type == 'next_year':
                    delivery_date = (now + relativedelta(years=1)).replace(hour=9, minute=0, second=0, microsecond=0)
                elif date_type == 'this_year':
                    delivery_date = now.replace(month=6, day=15, hour=9, minute=0, second=0, microsecond=0)  # Mid-year
                elif date_type == 'days_ahead':
                    # Extract number of days
                    days_match = re.search(r'(\d+)', match.group())
                    if days_match:
                        days = int(days_match.group(1))
                        delivery_date = (now + timedelta(days=days)).replace(hour=9, minute=0, second=0, microsecond=0)
                elif date_type == 'weeks_ahead':
                    # Extract number of weeks
                    weeks_match = re.search(r'(\d+)', match.group())
                    if weeks_match:
                        weeks = int(weeks_match.group(1))
                        delivery_date = (now + timedelta(weeks=weeks)).replace(hour=9, minute=0, second=0, microsecond=0)
                elif date_type == 'months_ahead':
                    # Extract number of months
                    months_match = re.search(r'(\d+)', match.group())
                    if months_match:
                        months = int(months_match.group(1))
                        delivery_date = (now + relativedelta(months=months)).replace(hour=9, minute=0, second=0, microsecond=0)
                elif date_type == 'next_day_of_week':
                    # Extract day name from "next monday", "next tuesday", etc.
                    day_match = re.search(r'next (\w+)', match.group(), re.IGNORECASE)
                    if day_match:
                        day_name = day_match.group(1).lower()
                        day_mapping = {
                            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                            'friday': 4, 'saturday': 5, 'sunday': 6,
                            'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6
                        }
                        if day_name in day_mapping:
                            target_day = day_mapping[day_name]
                            # For "next monday", we always want the next occurrence, so add 7 days minimum
                            days_ahead = (target_day - now.weekday()) % 7
                            if days_ahead == 0:
                                days_ahead = 7  # Same day next week
                            else:
                                days_ahead += 7  # Next week's occurrence
                            delivery_date = (now + timedelta(days=days_ahead)).replace(hour=9, minute=0, second=0, microsecond=0)
                elif date_type == 'day_of_week':
                    # Extract day name
                    day_match = re.search(r'on (\w+)', match.group(), re.IGNORECASE)
                    if day_match:
                        day_name = day_match.group(1).lower()
                        day_mapping = {
                            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                            'friday': 4, 'saturday': 5, 'sunday': 6,
                            'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6
                        }
                        if day_name in day_mapping:
                            target_day = day_mapping[day_name]
                            days_ahead = (target_day - now.weekday()) % 7
                            if days_ahead == 0:
                                days_ahead = 7  # Next week
                            delivery_date = (now + timedelta(days=days_ahead)).replace(hour=9, minute=0, second=0, microsecond=0)
                elif date_type == 'time':
                    # Extract time - handle both "at" and "for" cases
                    time_match = re.search(r'(?:at|for)\s+(\d{1,2}):(\d{2})(?::(\d{2}))?(?:\s*(am|pm|a\.m\.|p\.m\.))?', match.group(), re.IGNORECASE)
                    if not time_match:
                        # Fallback: try to extract time without "at" or "for"
                        time_match = re.search(r'(\d{1,2}):(\d{2})(?::(\d{2}))?(?:\s*(am|pm|a\.m\.|p\.m\.))?', match.group(), re.IGNORECASE)
                    if time_match:
                        hour = int(time_match.group(1))
                        minute = int(time_match.group(2))
                        ampm = time_match.group(4)
                        
                        # Handle AM/PM
                        if ampm:
                            ampm_lower = ampm.lower().replace('.', '')  # Remove dots for comparison
                            if ampm_lower == 'pm' and hour != 12:
                                hour += 12
                            elif ampm_lower == 'am' and hour == 12:
                                hour = 0
                        
                        # If we already have a date, just update the time
                        if delivery_date:
                            delivery_date = delivery_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                        else:
                            # Default to today with the specified time
                            delivery_date = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                            # If the time has passed today, set it for tomorrow
                            if delivery_date <= now:
                                delivery_date += timedelta(days=1)
        
        # Parse time references
        for pattern, time_type in time_patterns.items():
            if re.search(pattern, content_lower):
                date_info['time_reference'] = time_type
                if delivery_date:
                    # Update the time based on the reference
                    if time_type == 'morning':
                        delivery_date = delivery_date.replace(hour=9, minute=0, second=0, microsecond=0)
                    elif time_type == 'afternoon':
                        delivery_date = delivery_date.replace(hour=14, minute=0, second=0, microsecond=0)
                    elif time_type == 'evening':
                        delivery_date = delivery_date.replace(hour=18, minute=0, second=0, microsecond=0)
                    elif time_type == 'night':
                        delivery_date = delivery_date.replace(hour=20, minute=0, second=0, microsecond=0)
                    elif time_type == 'noon':
                        delivery_date = delivery_date.replace(hour=12, minute=0, second=0, microsecond=0)
                    elif time_type == 'midnight':
                        delivery_date = delivery_date.replace(hour=0, minute=0, second=0, microsecond=0)
                break
        
        # Clean the content by removing date references for better processing
        cleaned_content = content
        for original_text in date_info['original_text']:
            # Replace with a more natural version
            if 'tomorrow' in original_text.lower():
                cleaned_content = re.sub(r'\btomorrow\b', 'on the scheduled date', cleaned_content, flags=re.IGNORECASE)
            elif 'today' in original_text.lower():
                cleaned_content = re.sub(r'\btoday\b', 'on the scheduled date', cleaned_content, flags=re.IGNORECASE)
            elif 'tonight' in original_text.lower():
                cleaned_content = re.sub(r'\btonight\b', 'on the scheduled date', cleaned_content, flags=re.IGNORECASE)
        
        return delivery_date, cleaned_content, date_info

    def process_memory(self, content: str) -> Dict[str, Any]:
        """
        Process memory content with AI to extract insights and set delivery date
        """
        if not self.is_available():
            return {
                'summary': '',
                'tags': [],
                'memory_type': 'general',
                'importance': 5,
                'reasoning': 'AI service not available'
            }
        
        # Parse date references first
        delivery_date, cleaned_content, date_info = self.parse_date_references(content)
        
        prompt = f"""
        Analyze this memory content and provide insights:
        
        Original content: "{content}"
        Cleaned content: "{cleaned_content}"
        Date info: {date_info}
        
        Provide a JSON response with:
        {{
            "summary": "Brief summary of the memory",
            "tags": ["tag1", "tag2", "tag3"],
            "memory_type": "general|work|personal|learning|idea|reminder",
            "importance": 1-10,
            "reasoning": "Why this categorization was chosen",
            "delivery_date": "{delivery_date.isoformat() if delivery_date else None}",
            "delivery_type": "immediate|scheduled|recurring|conditional",
            "date_context": "Explanation of the date/time context"
        }}
        
        Memory type guidelines:
        - general: General memories and thoughts
        - work: Work-related tasks, meetings, deadlines
        - personal: Personal life, family, friends
        - learning: Educational content, skills, knowledge
        - idea: Creative ideas, inventions, concepts
        - reminder: Tasks, appointments, things to remember
        
        Importance guidelines:
        - 1-3: Low priority, casual notes
        - 4-6: Medium priority, worth remembering
        - 7-8: High priority, important tasks
        - 9-10: Critical, urgent matters
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Override delivery_date if we parsed one
            if delivery_date:
                result['delivery_date'] = delivery_date
                result['delivery_type'] = 'scheduled'
                if date_info['is_recurring']:
                    result['delivery_type'] = 'recurring'
            else:
                # Ensure we don't have string "None" values
                result['delivery_date'] = None
            
            # Only allow summaries for memories with long content (>= 200 characters)
            content_length = len((content or '').strip())
            if content_length < 200:
                result['summary'] = ''
            
            return result
            
        except Exception as e:
            # Fallback processing
            fallback_result = {
                'summary': f"Memory about: {content[:100]}...",
                'tags': ['memory'],
                'memory_type': 'general',
                'importance': 5,
                'reasoning': f'Fallback processing due to error: {str(e)}',
                'delivery_date': delivery_date,
                'delivery_type': 'scheduled' if delivery_date else 'immediate',
                'date_context': f"Date parsing: {date_info}"
            }
            
            if delivery_date:
                fallback_result['delivery_date'] = delivery_date
                fallback_result['delivery_type'] = 'scheduled'
                if date_info['is_recurring']:
                    fallback_result['delivery_type'] = 'recurring'
            else:
                # Ensure we don't have string "None" values
                fallback_result['delivery_date'] = None

            # Apply the same summary restriction on fallback
            content_length = len((content or '').strip())
            if content_length < 200:
                fallback_result['summary'] = ''
            
            return fallback_result
    
    def search_memories(self, query: str, memories: List[Dict]) -> List[Dict]:
        """
        Use ChatGPT to semantically search through memories
        """
        if not memories:
            return []
        
        if not self.is_available():
            # Fallback to simple keyword search if API is not available
            query_lower = query.lower()
            return [
                memory for memory in memories
                if query_lower in memory['content'].lower() or
                any(query_lower in tag.lower() for tag in memory['tags'])
            ]
        
        # Create context from memories with delivery dates
        memory_context_parts = []
        for i, memory in enumerate(memories):
            delivery_info = ""
            if memory.get('delivery_date'):
                delivery_info = f" (Scheduled for: {memory['delivery_date']})"
            memory_context_parts.append(
                f"Memory {i+1} (ID: {memory.get('id', i)}): {memory['content'][:200]}... (Tags: {', '.join(memory['tags'])}){delivery_info}"
            )
        
        memory_context = "\n\n".join(memory_context_parts)
        
        # Check for date-specific queries
        query_lower = query.lower()
        date_keywords = ['today', 'tonight', 'tomorrow', 'yesterday', 'this week', 'next week', 'this month', 'next month']
        has_date_reference = any(keyword in query_lower for keyword in date_keywords)
        
        prompt = f"""
        Given the search query: "{query}"
        Query contains date reference: {has_date_reference}
        
        And these memories:
        {memory_context}
        
        Return the indices of the most relevant memories (0-based) as a JSON array.
        Consider semantic similarity, not just exact keyword matches.
        
        IMPORTANT: If the query mentions a specific date/time (like "tomorrow", "today", "next week"), 
        prioritize memories that are scheduled for that specific period (check delivery_date).
        
        Example response: [0, 3, 7]
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=100
            )
            
            relevant_indices = json.loads(response.choices[0].message.content)
            return [memories[i] for i in relevant_indices if i < len(memories)]
        except Exception as e:
            # Fallback to simple keyword search
            query_lower = query.lower()
            return [
                memory for memory in memories
                if query_lower in memory['content'].lower() or
                any(query_lower in tag.lower() for tag in memory['tags'])
            ]
    
    def generate_memory_suggestions(self, user_memories: List[Dict]) -> List[str]:
        """
        Generate memory suggestions based on user's existing memories
        """
        if not user_memories:
            return [
                "What did you learn today?",
                "Any important meetings or conversations?",
                "What ideas came to mind?",
                "Any personal milestones to remember?"
            ]
        
        if not self.is_available():
            return [
                "What's the next step for your current projects?",
                "Any insights from today's experiences?",
                "What would you like to remember about this week?"
            ]
        
        # Analyze recent memories to generate suggestions
        recent_content = "\n".join([
            memory['content'][:100] for memory in user_memories[:5]
        ])
        
        prompt = f"""
        Based on these recent memories:
        {recent_content}
        
        Generate 3-5 thoughtful questions or prompts that might help the user
        remember related or follow-up information. Make them specific and actionable.
        
        IMPORTANT: If the user asks about a specific date or time (like "tonight", "tomorrow", "9:00"), 
        focus on memories related to that specific time period. For general time references without 
        specific context, ask for clarification rather than showing irrelevant suggestions.
        
        Return as a JSON array of strings.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300
            )
            
            suggestions = json.loads(response.choices[0].message.content)
            
            # Ensure we have a list of strings
            if isinstance(suggestions, list):
                return [str(s) for s in suggestions if s]
            else:
                raise ValueError("Response is not a list")
                
        except Exception as e:
            print(f"Error in generate_memory_suggestions: {e}")
            return [
                "What's the next step for your current projects?",
                "Any insights from today's experiences?",
                "What would you like to remember about this week?"
            ]

    def generate_contextual_suggestions(self, query: str, user_memories: List[Dict]) -> List[str]:
        """
        Generate contextual suggestions based on user query and memory context
        """
        if not self.is_available():
            return [
                "What's the next step for your current projects?",
                "Any insights from today's experiences?",
                "What would you like to remember about this week?"
            ]
        
        # Extract date/time context from query
        query_lower = query.lower()
        date_keywords = {
            'today': 'today',
            'tonight': 'today',
            'tomorrow': 'tomorrow', 
            'yesterday': 'yesterday',
            'this week': 'this week',
            'next week': 'next week',
            'this month': 'this month',
            'next month': 'next month'
        }
        
        # Check if query contains specific date references
        detected_date = None
        for keyword, date_type in date_keywords.items():
            if keyword in query_lower:
                detected_date = date_type
                break
        
        # If no specific date detected, ask for clarification
        if not detected_date and any(word in query_lower for word in ['plan', 'schedule', 'appointment', 'meeting', 'reminder']):
            return [
                "Could you specify which date you're asking about? (e.g., 'today', 'tomorrow', 'next week')",
                "I can help you find plans for a specific date. When are you looking for?",
                "To show you relevant memories, please mention a specific time period."
            ]
        
        # Filter memories based on detected date for better context
        relevant_memories = user_memories
        if detected_date:
            from django.utils import timezone
            import datetime
            
            today = timezone.now().date()
            date_filtered_memories = []
            
            for memory in user_memories:
                if memory.get('delivery_date'):
                    try:
                        # Parse delivery date from ISO string or datetime object
                        if isinstance(memory['delivery_date'], str):
                            from datetime import datetime as dt
                            delivery_date = dt.fromisoformat(memory['delivery_date'].replace('Z', '+00:00')).date()
                        else:
                            delivery_date = memory['delivery_date'].date()
                        
                        # Filter based on detected date
                        if detected_date == 'today' and delivery_date == today:
                            date_filtered_memories.append(memory)
                        elif detected_date == 'tomorrow' and delivery_date == today + datetime.timedelta(days=1):
                            date_filtered_memories.append(memory)
                        elif detected_date == 'yesterday' and delivery_date == today - datetime.timedelta(days=1):
                            date_filtered_memories.append(memory)
                        # Add more date filtering as needed
                    except (ValueError, TypeError, AttributeError):
                        # If parsing fails, skip this memory for date filtering
                        pass
            
            # Use filtered memories if we found date-specific ones, otherwise show fewer recent memories
            if date_filtered_memories:
                relevant_memories = date_filtered_memories
            elif detected_date:
                # If no memories for specific date, show only 3 recent memories to avoid confusion
                relevant_memories = user_memories[:3]
        
        # Enhanced memory context with delivery dates
        memory_context_parts = []
        for memory in relevant_memories[:10]:
            delivery_info = ""
            if memory.get('delivery_date'):
                # Format the delivery date more clearly
                try:
                    if isinstance(memory['delivery_date'], str):
                        from datetime import datetime as dt
                        delivery_dt = dt.fromisoformat(memory['delivery_date'].replace('Z', '+00:00'))
                        delivery_info = f" (Scheduled for: {delivery_dt.strftime('%B %d, %Y')})"
                    else:
                        delivery_info = f" (Scheduled for: {memory['delivery_date'].strftime('%B %d, %Y')})"
                except (ValueError, TypeError, AttributeError):
                    delivery_info = f" (Scheduled for: {memory['delivery_date']})"
            memory_context_parts.append(
                f"Memory: {memory['content'][:150]}... (Tags: {', '.join(memory.get('tags', []))}){delivery_info}"
            )
        
        memory_context = "\n".join(memory_context_parts)
        
        prompt = f"""
        User query: "{query}"
        Detected date context: {detected_date if detected_date else 'None'}
        Current date: {timezone.now().strftime('%B %d, %Y')}
        
        User's memories (filtered by date relevance when applicable):
        {memory_context}
        
        Based on the user's query and memory context:
        
        1. If the query mentions a specific date/time (like "tomorrow", "today", "next week"), 
           focus ONLY on memories that match that specific date context
        2. If no memories match the date context, acknowledge this and suggest creating a new memory for that date
        3. Generate 2-3 relevant suggestions that are specific to the user's requested date context
        4. When referencing dates in your suggestions, use the ACTUAL date the user is asking about (e.g., if they ask about "today", use today's actual date)
        
        CRITICAL RULES:
        - If user asks about "today", reference TODAY'S date ({timezone.now().strftime('%B %d, %Y')}) in suggestions
        - If user asks about "tonight", treat it as today ({timezone.now().strftime('%B %d, %Y')})
        - DO NOT include delivery dates from the memory context in your suggestions
        - Focus on the content and themes of memories, not their scheduled dates
        - If no memories match the requested date, suggest creating new memories for that specific date
        
        IMPORTANT: Return ONLY a valid JSON array of strings. Example: ["suggestion 1", "suggestion 2", "suggestion 3"]
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=200
            )
            
            suggestions = json.loads(response.choices[0].message.content)
            
            # Ensure we have a list of strings
            if isinstance(suggestions, list):
                return [str(s) for s in suggestions if s]
            else:
                raise ValueError("Response is not a list")
                
        except Exception as e:
            print(f"Error in generate_contextual_suggestions: {e}")
            # Return fallback suggestions instead of empty list
            if detected_date:
                return [
                    f"What do you have planned for {detected_date}?",
                    f"Any important events coming up {detected_date}?",
                    f"What would you like to remember about {detected_date}?"
                ]
            else:
                return [
                    "What's the next step for your current projects?",
                    "Any insights from today's experiences?",
                    "What would you like to remember about this week?"
                ] 