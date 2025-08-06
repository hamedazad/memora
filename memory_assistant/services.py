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
        Process a memory using advanced AI to generate summary, tags, auto-categorize, and extract dates
        """
        if not self.is_available():
            # Return fallback values if API is not available
            # Still try to extract dates even without AI
            from .date_recognition_service import date_recognition_service
            date_analysis = date_recognition_service.analyze_text_for_date_context(content)
            
            return {
                "summary": f"Memory about: {content[:100]}...",
                "tags": ["general"],
                "importance": 5,
                "memory_type": "general",
                "extracted_date": date_analysis.get('date'),
                "date_analysis": date_analysis
            }
        
        # Use the more advanced AI service for better categorization
        try:
            from .ai_services import get_ai_service
            ai_service = get_ai_service()
            result = ai_service.auto_categorize_memory(content)
            
            # Map the AI result to our expected format
            return {
                "summary": result.get("summary", f"Memory about: {content[:100]}..."),
                "tags": result.get("tags", ["general"]),
                "importance": result.get("importance", 5),
                "memory_type": result.get("category", "general"),
                "extracted_date": result.get("extracted_date"),
                "date_analysis": result.get("date_analysis", {}),
                "ai_reasoning": result.get("reasoning", "")
            }
        except Exception as e:
            # Fallback to the original method if AI service fails
            # Still try to extract dates
            from .date_recognition_service import date_recognition_service
            date_analysis = date_recognition_service.analyze_text_for_date_context(content)
            
            prompt = f"""
            Analyze the following memory content and provide:
            1. A concise summary (2-3 sentences)
            2. Relevant tags (5-8 tags as a JSON array)
            3. Importance level (1-10, where 10 is most important)
            4. Memory type - categorize into one of these:
               - work: Professional tasks, meetings, projects, career-related items
               - personal: Family, friends, hobbies, personal life, relationships
               - learning: Education, skills, courses, knowledge acquisition
               - idea: Creative thoughts, innovations, concepts, brainstorming
               - reminder: Tasks, to-dos, appointments, deadlines
               - general: Everything else
            
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
                    messages=[
                        {"role": "system", "content": "You are an expert at categorizing and analyzing personal memories. Be accurate and consistent in your categorization."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                
                result = json.loads(response.choices[0].message.content)
                result["extracted_date"] = date_analysis.get('date')
                result["date_analysis"] = date_analysis
                return result
            except Exception as e2:
                # Final fallback values if all AI methods fail
                return {
                    "summary": f"Memory about: {content[:100]}...",
                    "tags": ["general"],
                    "importance": 5,
                    "memory_type": "general",
                    "extracted_date": date_analysis.get('date'),
                    "date_analysis": date_analysis
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
                "What did you learn today that you want to remember?",
                "Any important conversations or insights from today?",
                "What's one thing you accomplished that you're proud of?",
                "Any ideas or thoughts that came to mind today?",
                "What would you like to remember about this week?"
            ]
        
        if not self.is_available():
            # Generate contextual fallback suggestions based on existing memories
            return self._generate_fallback_suggestions(user_memories)
        
        # Analyze recent memories to generate suggestions
        recent_content = "\n".join([
            f"Memory: {memory.get('content', '')[:150]}... (Tags: {', '.join(memory.get('tags', []))})"
            for memory in user_memories[:8]  # Use more memories for better context
        ])
        
        prompt = f"""
        Based on these recent memories:
        {recent_content}
        
        Generate 4-6 thoughtful, specific, and actionable questions or prompts that would help the user
        remember related or follow-up information. Make them:
        - Specific to their current patterns and interests
        - Actionable and practical
        - Varied in scope (daily, weekly, project-based)
        - Relevant to their recent activities
        
        Focus on:
        - Follow-up actions from recent memories
        - Related topics they might want to explore
        - Important details they might have missed
        - Future planning based on current activities
        
        CRITICAL: You must respond with ONLY a valid JSON array. No other text.
        Format: ["suggestion1", "suggestion2", "suggestion3", "suggestion4"]
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at helping people remember and organize their thoughts. You must ALWAYS respond with valid JSON arrays only. Never include explanatory text or formatting outside the JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            try:
                content = response.choices[0].message.content.strip()
                
                # Try to fix common JSON issues
                if content.startswith('[') and not content.endswith(']'):
                    # Add missing closing bracket
                    content += ']'
                elif not content.startswith('[') and content.endswith(']'):
                    # Add missing opening bracket
                    content = '[' + content
                elif not content.startswith('[') and not content.endswith(']'):
                    # Wrap in brackets if neither present
                    content = '[' + content + ']'
                
                suggestions = json.loads(content)
                # Ensure we return a list of strings
                if isinstance(suggestions, list):
                    return [str(s).strip() for s in suggestions if s and str(s).strip()]
                else:
                    return self._generate_fallback_suggestions(user_memories)
                    
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"Raw content: {response.choices[0].message.content}")
                
                # Try to parse as comma-separated values
                content = response.choices[0].message.content.strip()
                
                # Remove any JSON-like formatting
                if content.startswith('['):
                    content = content[1:]
                if content.endswith(']'):
                    content = content[:-1]
                
                # Split by comma and clean up
                suggestions = []
                for item in content.split(','):
                    item = item.strip().strip('"\'')
                    if item and len(item) > 5:  # Only include meaningful suggestions
                        suggestions.append(item)
                
                if suggestions:
                    return suggestions
                else:
                    return self._generate_fallback_suggestions(user_memories)
                
        except Exception as e:
            print(f"Error generating AI suggestions: {e}")
            return self._generate_fallback_suggestions(user_memories)
    
    def _generate_fallback_suggestions(self, user_memories: List[Dict]) -> List[str]:
        """
        Generate contextual fallback suggestions when AI is not available
        """
        suggestions = []
        
        # Analyze memory patterns to generate contextual suggestions
        all_content = " ".join([memory.get('content', '') for memory in user_memories])
        all_tags = []
        for memory in user_memories:
            all_tags.extend(memory.get('tags', []))
        
        # Check for common themes
        content_lower = all_content.lower()
        
        # Work-related suggestions
        if any(word in content_lower for word in ['meeting', 'project', 'work', 'client', 'deadline', 'task']):
            suggestions.extend([
                "What's the next step for your current work projects?",
                "Any follow-up actions needed from recent meetings?",
                "What deadlines are coming up this week?"
            ])
        
        # Learning-related suggestions
        if any(word in content_lower for word in ['learn', 'study', 'course', 'skill', 'knowledge', 'read']):
            suggestions.extend([
                "What did you learn today that you want to remember?",
                "Any insights from your recent learning activities?",
                "What skills would you like to develop further?"
            ])
        
        # Personal-related suggestions
        if any(word in content_lower for word in ['family', 'friend', 'personal', 'hobby', 'relationship']):
            suggestions.extend([
                "Any important personal events or conversations to remember?",
                "What personal goals are you working towards?",
                "Any family or friend activities you want to plan?"
            ])
        
        # Idea-related suggestions
        if any(word in content_lower for word in ['idea', 'creative', 'innovation', 'concept', 'thought']):
            suggestions.extend([
                "What creative ideas have you had recently?",
                "Any innovative solutions you've been thinking about?",
                "What problems are you trying to solve?"
            ])
        
        # Add general suggestions if we don't have enough
        if len(suggestions) < 3:
            suggestions.extend([
                "What's one thing you accomplished today that you're proud of?",
                "Any important insights or realizations from this week?",
                "What would you like to remember about this month?"
            ])
        
        # Add tag-based suggestions
        if all_tags:
            unique_tags = list(set(all_tags))[:3]
            for tag in unique_tags:
                suggestions.append(f"What's new with your {tag} activities?")
        
        # Ensure we return 4-6 suggestions
        return suggestions[:6] 