import os
import json
from typing import List, Dict, Any
from openai import OpenAI
from django.conf import settings
from dotenv import load_dotenv

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
    
    def process_memory(self, content: str) -> Dict[str, Any]:
        """
        Process a memory using ChatGPT to generate summary and tags
        """
        if not self.is_available():
            # Return fallback values if API is not available
            return {
                "summary": f"Memory about: {content[:100]}...",
                "tags": ["general"],
                "importance": 5,
                "memory_type": "general"
            }
        
        prompt = f"""
        Analyze the following memory content and provide:
        1. A concise summary (2-3 sentences)
        2. Relevant tags (5-8 tags as a JSON array)
        3. Importance level (1-10, where 10 is most important)
        4. Memory type (general, work, personal, learning, idea, reminder)
        
        Memory content: {content}
        
        Respond in JSON format:
        {{
            "summary": "summary text",
            "tags": ["tag1", "tag2", "tag3"],
            "importance": 7,
            "memory_type": "work"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            # Fallback values if API fails
            return {
                "summary": f"Memory about: {content[:100]}...",
                "tags": ["general"],
                "importance": 5,
                "memory_type": "general"
            }
    
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
        
        # Create context from memories
        memory_context = "\n\n".join([
            f"Memory {i+1} (ID: {memory.get('id', i)}): {memory['content'][:200]}... (Tags: {', '.join(memory['tags'])})"
            for i, memory in enumerate(memories)
        ])
        
        prompt = f"""
        Given the search query: "{query}"
        
        And these memories:
        {memory_context}
        
        Return the indices of the most relevant memories (0-based) as a JSON array.
        Consider semantic similarity, not just exact keyword matches.
        
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
                "Any personal achievements to remember?"
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
            return suggestions
        except Exception as e:
            return [
                "What's the next step for your current projects?",
                "Any insights from today's experiences?",
                "What would you like to remember about this week?"
            ] 