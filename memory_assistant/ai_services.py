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
            
            system_prompt = "You are a helpful assistant that categorizes memories. Return only 3-5 relevant categories as a comma-separated list."
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
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
    
    def generate_memory_suggestions(self, user_memories: List[str]) -> List[str]:
        """Generate suggestions for new memories based on existing ones."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            # Analyze recent memories to generate suggestions
            recent_memories = "\n".join(user_memories[-5:])  # Last 5 memories
            
            system_prompt = "You are a helpful assistant that suggests new memory topics based on existing memories. Return 3-5 suggestions as a comma-separated list."
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Based on these recent memories, suggest new topics to remember: {recent_memories}"}
                ],
                max_tokens=150,
                temperature=0.6
            )
            suggestions = response.choices[0].message.content.strip().split(',')
            return [suggestion.strip() for suggestion in suggestions]
        except Exception as e:
            print(f"Error in generate_memory_suggestions: {e}")
            return ["Unable to generate suggestions at this time."]
    
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
        """Automatically categorize a memory with advanced AI recognition."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            prompt = f"""
            Analyze the following memory content and categorize it with high precision. You MUST analyze:
            1. MEMORY TYPE based on content and purpose
            2. IMPORTANCE LEVEL based on urgency, significance, and impact
            3. SCHEDULING NEEDS based on time-sensitive elements
            4. TAGS for better organization
            5. SUMMARY for quick understanding

            CATEGORY DEFINITIONS:
            - work: Professional tasks, meetings, projects, career-related items, business activities, job responsibilities, workplace events, professional development, work deadlines, team activities, client interactions, business ideas, work-related learning
            - personal: Family, friends, hobbies, personal life, relationships, social events, personal celebrations, family activities, personal interests, social gatherings, personal goals, lifestyle choices, personal experiences
            - learning: Education, skills, courses, knowledge acquisition, academic activities, training sessions, reading notes, study materials, educational goals, skill development, research, tutorials, workshops, certifications
            - idea: Creative thoughts, innovations, concepts, brainstorming, creative projects, inventions, artistic ideas, business concepts, problem-solving ideas, innovative solutions, creative inspiration, design ideas
            - reminder: Tasks, to-dos, appointments, deadlines, scheduled events, time-sensitive activities, future plans, calendar events, action items, follow-ups, time management, planning activities
            - general: Everything else that doesn't fit the above categories

            IMPORTANCE SCALE (be specific about reasoning):
            - 1-2: Trivial notes, casual observations, low-priority items
            - 3-4: Useful information, minor tasks, interesting but not critical
            - 5-6: Important memories, regular tasks, significant personal events
            - 7-8: High-priority items, important deadlines, significant work/personal matters
            - 9-10: Critical/urgent matters, major deadlines, life-changing events, emergencies

            SCHEDULING ANALYSIS:
            Look for time indicators like: today, tomorrow, next week, specific dates, deadlines, appointments, recurring events, "need to", "must do", "don't forget", urgency words

            Memory content: {content}

            Provide a comprehensive analysis in JSON format:
            {{
                "category": "work|personal|learning|idea|reminder|general",
                "confidence": 0-100,
                "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
                "summary": "Clear 1-2 sentence summary",
                "importance": 1-10,
                "reasoning": "Detailed explanation of categorization and importance",
                "is_time_sensitive": true/false,
                "urgency_level": "low|medium|high|critical",
                "suggested_delivery_type": "immediate|scheduled|recurring",
                "key_themes": ["theme1", "theme2", "theme3"]
            }}
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert AI memory analyst with deep understanding of human activities and categorization. You excel at identifying the primary purpose, urgency, and context of memories. Be precise, consistent, and provide well-reasoned categorizations. ALWAYS fill in all required fields with thoughtful analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
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
            
            # Ensure required fields exist
            result['tags'] = result.get('tags', ['general'])
            result['summary'] = result.get('summary', f"Memory: {content[:100]}...")
            result['reasoning'] = result.get('reasoning', 'AI-generated categorization')
            result['is_time_sensitive'] = result.get('is_time_sensitive', False)
            result['urgency_level'] = result.get('urgency_level', 'low')
            result['suggested_delivery_type'] = result.get('suggested_delivery_type', 'immediate')
            result['key_themes'] = result.get('key_themes', [])
            
            return result
        except Exception as e:
            print(f"Error in auto_categorize_memory: {e}")
            return {
                "category": "general",
                "confidence": 50,
                "tags": ["general"],
                "summary": f"Memory about: {content[:100]}...",
                "importance": 5,
                "reasoning": "Fallback categorization due to processing error",
                "is_time_sensitive": False,
                "urgency_level": "low",
                "suggested_delivery_type": "immediate",
                "key_themes": []
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