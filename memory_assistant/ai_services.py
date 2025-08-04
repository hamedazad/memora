"""
AI Services for Memory Assistant

This module provides AI-powered features for the memory assistant app.
"""

import os
from typing import List, Dict, Optional
from django.conf import settings

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
    
    def generate_memory_suggestions(self, user_memories: List[str]) -> List[str]:
        """Generate suggestions for new memories based on existing ones."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            # Analyze recent memories to generate suggestions
            recent_memories = "\n".join(user_memories[-5:])  # Last 5 memories
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that suggests new memory topics based on existing memories. Return 3-5 suggestions as a comma-separated list."},
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