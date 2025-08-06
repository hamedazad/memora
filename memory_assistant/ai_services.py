"""
AI Services for Memory Assistant

This module provides AI-powered features for the memory assistant app.
"""

import os
from typing import List, Dict, Optional, Any
from django.conf import settings
import json

class AIService:
    """AI service for memory processing and analysis."""
    
    def __init__(self):
        # Force reload environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")
    
    def auto_categorize(self, content: str) -> List[str]:
        """Automatically categorize a memory based on its content."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that categorizes memories. Return only 3-5 relevant categories as a comma-separated list."},
                    {"role": "user", "content": f"Categorize this memory: {content}"}
                ],
                max_tokens=50,
                temperature=0.3
            )
            categories = response.choices[0].message.content.strip().split(',')
            return [cat.strip() for cat in categories]
        except Exception as e:
            print(f"Error in auto_categorize: {e}")
            return ["General"]
    
    def summarize_memory(self, content: str) -> str:
        """Create a concise summary of a memory."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise summaries. Keep summaries to 2-3 sentences maximum."},
                    {"role": "user", "content": f"Summarize this memory: {content}"}
                ],
                max_tokens=100,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error in summarize_memory: {e}")
            return content[:200] + "..." if len(content) > 200 else content
    
    def enhance_memory(self, content: str) -> str:
        """Suggest improvements to make a memory more detailed and useful."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that suggests improvements to make memories more detailed and useful. Provide specific suggestions."},
                    {"role": "user", "content": f"Suggest improvements for this memory: {content}"}
                ],
                max_tokens=200,
                temperature=0.5
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error in enhance_memory: {e}")
            return "Unable to generate suggestions at this time."
    
    def generate_tags(self, content: str) -> List[str]:
        """Generate relevant tags for a memory."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates relevant tags. Return only 3-5 tags as a comma-separated list."},
                    {"role": "user", "content": f"Generate tags for this memory: {content}"}
                ],
                max_tokens=50,
                temperature=0.3
            )
            tags = response.choices[0].message.content.strip().split(',')
            return [tag.strip() for tag in tags]
        except Exception as e:
            print(f"Error in generate_tags: {e}")
            return []
    
    def find_related_topics(self, content: str) -> List[str]:
        """Find related topics or themes in a memory."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that identifies related topics and themes. Return 3-5 related topics as a comma-separated list."},
                    {"role": "user", "content": f"Find related topics for this memory: {content}"}
                ],
                max_tokens=100,
                temperature=0.4
            )
            topics = response.choices[0].message.content.strip().split(',')
            return [topic.strip() for topic in topics]
        except Exception as e:
            print(f"Error in find_related_topics: {e}")
            return []
    
    def generate_memory_suggestions(self, user_memories: List[Dict]) -> List[str]:
        """Generate suggestions for new memories based on existing ones."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            # Format memories for better context
            formatted_memories = []
            for memory in user_memories[-8:]:  # Last 8 memories for better context
                if isinstance(memory, dict):
                    content = memory.get('content', '')
                    tags = memory.get('tags', [])
                    memory_type = memory.get('memory_type', 'general')
                    importance = memory.get('importance', 5)
                    formatted_memories.append(f"Type: {memory_type}, Importance: {importance}/10, Content: {content[:100]}..., Tags: {', '.join(tags)}")
                else:
                    formatted_memories.append(str(memory))
            
            recent_memories = "\n".join(formatted_memories)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at helping people remember and organize their thoughts. You must ALWAYS respond with valid JSON arrays only. Never include explanatory text or formatting outside the JSON."},
                    {"role": "user", "content": f"Based on these recent memories, suggest 4-6 new topics to remember. Return ONLY a JSON array: {recent_memories}"}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            try:
                content = response.choices[0].message.content.strip()
                
                # Try to fix common JSON issues
                if content.startswith('[') and not content.endswith(']'):
                    content += ']'
                elif not content.startswith('[') and content.endswith(']'):
                    content = '[' + content
                elif not content.startswith('[') and not content.endswith(']'):
                    content = '[' + content + ']'
                
                suggestions = json.loads(content)
                if isinstance(suggestions, list):
                    return [str(s).strip() for s in suggestions if s and str(s).strip()]
                else:
                    # Fallback to comma-separated parsing
                    suggestions = response.choices[0].message.content.strip().split(',')
                    return [suggestion.strip() for suggestion in suggestions if suggestion.strip()]
            except json.JSONDecodeError as e:
                print(f"AI Services JSON parsing error: {e}")
                print(f"Raw content: {response.choices[0].message.content}")
                
                # Fallback to comma-separated parsing
                content = response.choices[0].message.content.strip()
                
                # Remove any JSON-like formatting
                if content.startswith('['):
                    content = content[1:]
                if content.endswith(']'):
                    content = content[:-1]
                
                suggestions = []
                for item in content.split(','):
                    item = item.strip().strip('"\'')
                    if item and len(item) > 5:  # Only include meaningful suggestions
                        suggestions.append(item)
                
                return suggestions if suggestions else ["Unable to generate suggestions at this time."]
                
        except Exception as e:
            print(f"Error in generate_memory_suggestions: {e}")
            return [
                "What did you learn today that you want to remember?",
                "Any important conversations or insights from today?",
                "What's one thing you accomplished that you're proud of?",
                "Any ideas or thoughts that came to mind today?"
            ]
    
    def analyze_productivity_patterns(self, memories: List[Dict]) -> Dict:
        """Analyze productivity patterns from memories."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            # Extract key information from memories
            memory_text = "\n".join([f"Date: {m.get('created_at', 'Unknown')}, Content: {m.get('content', '')}" for m in memories[-10:]])
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes productivity patterns. Provide insights about memory creation patterns, themes, and suggestions for improvement."},
                    {"role": "user", "content": f"Analyze these memories for productivity patterns: {memory_text}"}
                ],
                max_tokens=300,
                temperature=0.4
            )
            return {
                "analysis": response.choices[0].message.content.strip(),
                "memory_count": len(memories),
                "recent_activity": len([m for m in memories if m.get('created_at')])
            }
        except Exception as e:
            print(f"Error in analyze_productivity_patterns: {e}")
            return {"analysis": "Unable to analyze patterns at this time.", "memory_count": len(memories)}

    def auto_categorize_memory(self, content: str) -> Dict[str, Any]:
        """Automatically categorize a memory with advanced AI recognition and date extraction."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            # First, extract date information using our date recognition service
            from .date_recognition_service import date_recognition_service
            date_analysis = date_recognition_service.analyze_text_for_date_context(content)
            
            prompt = f"""
            Analyze the following memory content and categorize it with high precision into one of these categories:

            CATEGORY DEFINITIONS:
            - work: Professional tasks, meetings, projects, career-related items, business activities, job responsibilities, workplace events, professional development, work deadlines, team activities, client interactions, business ideas, work-related learning
            - personal: Family, friends, hobbies, personal life, relationships, social events, personal celebrations, family activities, personal interests, social gatherings, personal goals, lifestyle choices, personal experiences
            - learning: Education, skills, courses, knowledge acquisition, academic activities, training sessions, reading notes, study materials, educational goals, skill development, research, tutorials, workshops, certifications
            - idea: Creative thoughts, innovations, concepts, brainstorming, creative projects, inventions, artistic ideas, business concepts, problem-solving ideas, innovative solutions, creative inspiration, design ideas
            - reminder: Tasks, to-dos, appointments, deadlines, scheduled events, time-sensitive activities, future plans, calendar events, action items, follow-ups, time management, planning activities
            - general: Everything else that doesn't fit the above categories

            ANALYSIS INSTRUCTIONS:
            1. Look for specific keywords and context clues
            2. Consider the intent and purpose of the memory
            3. Identify the primary focus of the content
            4. Consider temporal aspects (past events vs future plans)
            5. Evaluate the emotional and practical significance
            6. Pay special attention to time-sensitive content and scheduled events

            Memory content: {content}

            Provide a detailed analysis in JSON format:
            {{
                "category": "work|personal|learning|idea|reminder|general",
                "confidence": 0-100,
                "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
                "summary": "1-2 sentence summary",
                "importance": 1-10,
                "reasoning": "Brief explanation of why this category was chosen",
                "has_scheduled_date": true/false,
                "date_context": "Description of any date/time information found"
            }}
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert AI memory analyst with deep understanding of human activities and categorization. You excel at identifying the primary purpose and context of memories. Be precise, consistent, and provide well-reasoned categorizations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Ensure the category is valid
            valid_categories = ['work', 'personal', 'learning', 'idea', 'reminder', 'general']
            if result.get('category') not in valid_categories:
                result['category'] = 'general'
            
            # Ensure importance is within range
            importance = result.get('importance', 5)
            if not isinstance(importance, int) or importance < 1 or importance > 10:
                result['importance'] = 5
            
            # Add date information to the result
            result['extracted_date'] = date_analysis.get('date')
            result['date_analysis'] = date_analysis
            
            # If AI detected a scheduled date but our service didn't find one, 
            # or if our service found a date but AI didn't detect it, adjust accordingly
            ai_has_scheduled = result.get('has_scheduled_date', False)
            service_has_date = date_analysis.get('has_date', False)
            
            if service_has_date and not ai_has_scheduled:
                result['has_scheduled_date'] = True
                result['date_context'] = f"Detected date: {date_analysis.get('date')} ({date_analysis.get('date_type', 'unknown')})"
            elif ai_has_scheduled and not service_has_date:
                # AI detected a date but our service didn't - trust AI's judgment
                result['extracted_date'] = None
                result['date_analysis'] = {'has_date': False}
            
            return result
        except Exception as e:
            print(f"Error in auto_categorize_memory: {e}")
            # Fallback with date analysis
            from .date_recognition_service import date_recognition_service
            date_analysis = date_recognition_service.analyze_text_for_date_context(content)
            
            return {
                "category": "general",
                "confidence": 50,
                "tags": ["general"],
                "summary": f"Memory about: {content[:100]}...",
                "importance": 5,
                "reasoning": "Fallback categorization due to processing error",
                "extracted_date": date_analysis.get('date'),
                "date_analysis": date_analysis,
                "has_scheduled_date": date_analysis.get('has_date', False),
                "date_context": "Date analysis performed during fallback processing"
            }
    
    def categorize_audio_memory(self, audio_text: str) -> Dict[str, Any]:
        """Categorize audio-transcribed memory content with enhanced AI recognition."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            prompt = f"""
            This is a transcribed audio memory. Analyze and categorize it with high precision into one of these categories:

            CATEGORY DEFINITIONS:
            - work: Professional tasks, meetings, projects, career-related items, business activities, job responsibilities, workplace events, professional development, work deadlines, team activities, client interactions, business ideas, work-related learning
            - personal: Family, friends, hobbies, personal life, relationships, social events, personal celebrations, family activities, personal interests, social gatherings, personal goals, lifestyle choices, personal experiences
            - learning: Education, skills, courses, knowledge acquisition, academic activities, training sessions, reading notes, study materials, educational goals, skill development, research, tutorials, workshops, certifications
            - idea: Creative thoughts, innovations, concepts, brainstorming, creative projects, inventions, artistic ideas, business concepts, problem-solving ideas, innovative solutions, creative inspiration, design ideas
            - reminder: Tasks, to-dos, appointments, deadlines, scheduled events, time-sensitive activities, future plans, calendar events, action items, follow-ups, time management, planning activities
            - general: Everything else that doesn't fit the above categories

            ANALYSIS INSTRUCTIONS:
            1. Look for specific keywords and context clues in the audio transcription
            2. Consider the intent and purpose of the spoken memory
            3. Identify the primary focus of the content
            4. Consider temporal aspects (past events vs future plans)
            5. Evaluate the emotional and practical significance
            6. Account for potential transcription errors or unclear speech

            Audio transcription: {audio_text}

            Provide a detailed analysis in JSON format:
            {{
                "category": "work|personal|learning|idea|reminder|general",
                "confidence": 0-100,
                "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
                "summary": "1-2 sentence summary",
                "importance": 1-10,
                "reasoning": "Brief explanation of why this category was chosen"
            }}
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert AI memory analyst specializing in audio transcriptions. You excel at identifying the primary purpose and context of spoken memories, even with potential transcription errors. Be precise, consistent, and provide well-reasoned categorizations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Ensure the category is valid
            valid_categories = ['work', 'personal', 'learning', 'idea', 'reminder', 'general']
            if result.get('category') not in valid_categories:
                result['category'] = 'general'
            
            # Ensure importance is within range
            importance = result.get('importance', 5)
            if not isinstance(importance, int) or importance < 1 or importance > 10:
                result['importance'] = 5
            
            return result
        except Exception as e:
            print(f"Error in categorize_audio_memory: {e}")
            return {
                "category": "general",
                "confidence": 50,
                "tags": ["general"],
                "summary": f"Audio memory about: {audio_text[:100]}...",
                "importance": 5
            }

# Global AI service instance
ai_service = None

def get_ai_service():
    """Get or create AI service instance."""
    global ai_service
    if ai_service is None:
        try:
            ai_service = AIService()
        except ValueError:
            return None
    return ai_service 