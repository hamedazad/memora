import os
import json
import numpy as np
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from openai import OpenAI
from django.conf import settings
from django.db.models import Q, Count, Avg
from dotenv import load_dotenv

from .models import Memory, MemorySearch

load_dotenv()


class AIRecommendationService:
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
    
    def get_user_memory_patterns(self, user) -> Dict[str, Any]:
        """
        Analyze user's memory patterns to understand their preferences and behavior
        """
        memories = Memory.objects.filter(user=user, is_archived=False)
        
        if not memories.exists():
            return {
                'total_memories': 0,
                'favorite_types': [],
                'common_tags': [],
                'activity_patterns': {},
                'importance_distribution': {},
                'content_themes': []
            }
        
        # Memory type preferences
        type_counts = memories.values('memory_type').annotate(count=Count('id'))
        favorite_types = [item['memory_type'] for item in type_counts.order_by('-count')[:3]]
        
        # Tag analysis
        all_tags = []
        for memory in memories:
            all_tags.extend(memory.tags)
        tag_counts = Counter(all_tags)
        common_tags = [tag for tag, count in tag_counts.most_common(10)]
        
        # Activity patterns (time-based)
        recent_memories = memories.filter(
            created_at__gte=datetime.now() - timedelta(days=30)
        )
        # Use SQLite-compatible datetime extraction
        hourly_pattern = recent_memories.extra(
            select={'hour': "strftime('%H', created_at)"}
        ).values('hour').annotate(count=Count('id'))
        
        # Importance distribution
        importance_dist = memories.values('importance').annotate(count=Count('id'))
        importance_distribution = {
            str(item['importance']): item['count'] 
            for item in importance_dist
        }
        
        # Content themes (using AI if available)
        content_themes = self._analyze_content_themes(memories)
        
        return {
            'total_memories': memories.count(),
            'favorite_types': favorite_types,
            'common_tags': common_tags,
            'activity_patterns': {
                'hourly': {str(item['hour']): item['count'] for item in hourly_pattern},
                'recent_count': recent_memories.count()
            },
            'importance_distribution': importance_distribution,
            'content_themes': content_themes
        }
    
    def _analyze_content_themes(self, memories) -> List[str]:
        """Analyze memory content to identify recurring themes"""
        if not self.is_available() or not memories.exists():
            return ["general", "personal", "work"]
        
        # Sample recent memories for theme analysis
        sample_memories = memories.order_by('-created_at')[:10]
        content_sample = "\n".join([
            f"Memory {i+1}: {memory.content[:100]}..." 
            for i, memory in enumerate(sample_memories)
        ])
        
        prompt = f"""
        Analyze these memory contents and identify 5-8 recurring themes or topics:
        
        {content_sample}
        
        Return as a JSON array of theme names (e.g., ["work projects", "personal goals", "learning insights"]).
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            themes = json.loads(response.choices[0].message.content)
            return themes
        except Exception:
            return ["general", "personal", "work"]
    
    def get_personalized_recommendations(self, user) -> Dict[str, Any]:
        """
        Generate personalized recommendations based on user patterns
        """
        patterns = self.get_user_memory_patterns(user)
        
        if patterns['total_memories'] == 0:
            return {
                'memory_prompts': self._get_default_prompts(),
                'content_suggestions': [],
                'improvement_tips': [],
                'related_memories': [],
                'trending_topics': []
            }
        
        # Generate personalized memory prompts
        memory_prompts = self._generate_personalized_prompts(patterns)
        
        # Content suggestions based on patterns
        content_suggestions = self._generate_content_suggestions(patterns)
        
        # Improvement tips
        improvement_tips = self._generate_improvement_tips(patterns)
        
        # Find related memories
        related_memories = self._find_related_memories(user, patterns)
        
        # Identify trending topics
        trending_topics = self._identify_trending_topics(user, patterns)
        
        return {
            'memory_prompts': memory_prompts,
            'content_suggestions': content_suggestions,
            'improvement_tips': improvement_tips,
            'related_memories': related_memories,
            'trending_topics': trending_topics
        }
    
    def _get_default_prompts(self) -> List[str]:
        """Default prompts for new users"""
        return [
            "What's the most important thing that happened today?",
            "What did you learn that you want to remember?",
            "Any ideas or insights that came to mind?",
            "What are you grateful for today?",
            "What's your main goal for tomorrow?"
        ]
    
    def _generate_personalized_prompts(self, patterns: Dict) -> List[str]:
        """Generate personalized memory prompts based on user patterns"""
        if not self.is_available():
            return self._get_default_prompts()
        
        # Create context from user patterns
        context = f"""
        User Memory Patterns:
        - Favorite memory types: {', '.join(patterns['favorite_types'])}
        - Common tags: {', '.join(patterns['common_tags'][:5])}
        - Content themes: {', '.join(patterns['content_themes'][:3])}
        - Total memories: {patterns['total_memories']}
        """
        
        prompt = f"""
        Based on this user's memory patterns:
        {context}
        
        Generate 5 personalized memory prompts that would be most relevant and helpful for this user.
        Make them specific to their interests and patterns.
        
        Return as a JSON array of strings.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300
            )
            
            prompts = json.loads(response.choices[0].message.content)
            return prompts
        except Exception:
            return self._get_default_prompts()
    
    def _generate_content_suggestions(self, patterns: Dict) -> List[Dict[str, str]]:
        """Generate content suggestions based on user patterns"""
        suggestions = []
        
        # Suggest based on favorite types
        for memory_type in patterns['favorite_types']:
            if memory_type == 'work':
                suggestions.append({
                    'type': 'work',
                    'title': 'Work Progress Update',
                    'description': 'Track your current work projects and achievements'
                })
            elif memory_type == 'learning':
                suggestions.append({
                    'type': 'learning',
                    'title': 'Learning Insight',
                    'description': 'Document something new you learned today'
                })
            elif memory_type == 'personal':
                suggestions.append({
                    'type': 'personal',
                    'title': 'Personal Reflection',
                    'description': 'Reflect on your personal growth or experiences'
                })
        
        # Suggest based on common tags
        for tag in patterns['common_tags'][:3]:
            suggestions.append({
                'type': 'tagged',
                'title': f'Update on {tag.title()}',
                'description': f'Share progress or thoughts about {tag}'
            })
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _generate_improvement_tips(self, patterns: Dict) -> List[str]:
        """Generate improvement tips based on user patterns"""
        tips = []
        
        # Analyze patterns and provide tips
        if patterns['total_memories'] < 10:
            tips.append("Try to create at least one memory per day to build a habit")
        
        if not patterns['favorite_types']:
            tips.append("Explore different memory types to organize your thoughts better")
        
        if len(patterns['common_tags']) < 3:
            tips.append("Use tags to categorize your memories for easier searching")
        
        # Check importance distribution
        importance_dist = patterns['importance_distribution']
        if importance_dist:
            avg_importance = sum(
                int(level) * count for level, count in importance_dist.items()
            ) / sum(importance_dist.values())
            
            if avg_importance < 5:
                tips.append("Consider marking more memories as important to prioritize what matters")
            elif avg_importance > 8:
                tips.append("You're good at identifying important memories. Try adding more context to less important ones too")
        
        return tips if tips else ["Keep up the great work with your memory journaling!"]
    
    def _find_related_memories(self, user, patterns: Dict) -> List[Dict]:
        """Find memories that might be related to recent entries"""
        recent_memories = Memory.objects.filter(
            user=user, 
            is_archived=False
        ).order_by('-created_at')[:3]
        
        if not recent_memories.exists():
            return []
        
        # Find memories with similar tags or types
        related = []
        for recent in recent_memories:
            similar_memories = Memory.objects.filter(
                user=user,
                is_archived=False,
                created_at__lt=recent.created_at
            ).filter(
                Q(memory_type=recent.memory_type) |
                Q(tags__overlap=recent.tags)
            ).exclude(id=recent.id)[:2]
            
            for memory in similar_memories:
                related.append({
                    'id': memory.id,
                    'content': memory.content[:100] + "..." if len(memory.content) > 100 else memory.content,
                    'type': memory.memory_type,
                    'created_at': memory.created_at.strftime('%Y-%m-%d'),
                    'relevance': 'Similar tags or type'
                })
        
        return related[:5]  # Limit to 5 related memories
    
    def _identify_trending_topics(self, user, patterns: Dict) -> List[Dict]:
        """Identify trending topics in user's recent memories"""
        recent_memories = Memory.objects.filter(
            user=user,
            is_archived=False,
            created_at__gte=datetime.now() - timedelta(days=7)
        )
        
        if not recent_memories.exists():
            return []
        
        # Count recent tags
        recent_tags = []
        for memory in recent_memories:
            recent_tags.extend(memory.tags)
        
        tag_counts = Counter(recent_tags)
        trending = []
        
        for tag, count in tag_counts.most_common(5):
            if count > 1:  # Only include tags that appear multiple times
                trending.append({
                    'tag': tag,
                    'frequency': count,
                    'description': f'Appeared {count} times in the last week'
                })
        
        return trending
    
    def get_smart_search_suggestions(self, user, query: str) -> List[str]:
        """Generate smart search suggestions based on user's memories"""
        if not self.is_available():
            return []
        
        # Get user's memory context
        memories = Memory.objects.filter(user=user, is_archived=False)[:20]
        memory_context = "\n".join([
            f"Memory: {memory.content[:100]}... (Tags: {', '.join(memory.tags)})"
            for memory in memories
        ])
        
        prompt = f"""
        Based on this user's memories:
        {memory_context}
        
        And their search query: "{query}"
        
        Suggest 3-5 related search terms or questions that might help them find what they're looking for.
        Make suggestions specific to their memory content.
        
        Return as a JSON array of strings.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=200
            )
            
            suggestions = json.loads(response.choices[0].message.content)
            return suggestions
        except Exception:
            return []
    
    def get_memory_insights(self, user) -> Dict[str, Any]:
        """Generate insights about user's memory patterns and growth"""
        patterns = self.get_user_memory_patterns(user)
        
        if patterns['total_memories'] == 0:
            return {
                'insights': ["Start creating memories to see personalized insights!"],
                'growth_metrics': {},
                'recommendations': []
            }
        
        insights = []
        growth_metrics = {}
        
        # Memory growth over time
        memories = Memory.objects.filter(user=user, is_archived=False)
        if memories.count() > 1:
            first_memory = memories.order_by('created_at').first()
            last_memory = memories.order_by('created_at').last()
            days_active = (last_memory.created_at - first_memory.created_at).days
            
            if days_active > 0:
                avg_per_day = memories.count() / days_active
                growth_metrics['avg_memories_per_day'] = round(avg_per_day, 2)
                
                if avg_per_day >= 1:
                    insights.append("You're consistently creating memories - great habit!")
                elif avg_per_day >= 0.5:
                    insights.append("You're building a good memory journaling habit")
                else:
                    insights.append("Consider creating memories more frequently to build a stronger habit")
        
        # Memory type diversity
        type_counts = memories.values('memory_type').count()
        if type_counts >= 4:
            insights.append("You're using a good variety of memory types")
        elif type_counts >= 2:
            insights.append("Try exploring different memory types to better organize your thoughts")
        else:
            insights.append("Consider using different memory types to categorize your thoughts")
        
        # Tag usage
        if patterns['common_tags']:
            insights.append(f"Your most common topics are: {', '.join(patterns['common_tags'][:3])}")
        
        # Recent activity
        recent_count = patterns['activity_patterns']['recent_count']
        if recent_count >= 5:
            insights.append("You've been very active with memory creation recently!")
        elif recent_count == 0:
            insights.append("Consider creating a memory today to keep your journal active")
        
        return {
            'insights': insights,
            'growth_metrics': growth_metrics,
            'recommendations': self._generate_improvement_tips(patterns)
        } 