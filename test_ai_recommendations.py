#!/usr/bin/env python3
"""
Test script for AI recommendation features
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from django.contrib.auth.models import User
from memory_assistant.models import Memory
from memory_assistant.recommendation_service import AIRecommendationService
from datetime import datetime, timedelta

def test_ai_recommendations():
    """Test the AI recommendation service"""
    print("🤖 Testing AI Recommendation Service")
    print("=" * 50)
    
    # Initialize the service
    service = AIRecommendationService()
    
    # Check if AI is available
    print(f"AI Service Available: {service.is_available()}")
    
    if not service.is_available():
        print("❌ OpenAI API key not configured. Please set OPENAI_API_KEY in your .env file.")
        return
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com'}
    )
    
    if created:
        print(f"✅ Created test user: {user.username}")
    else:
        print(f"✅ Using existing test user: {user.username}")
    
    # Create some test memories if none exist
    if not Memory.objects.filter(user=user).exists():
        print("📝 Creating test memories...")
        
        test_memories = [
            {
                'content': 'Had a great meeting with the development team about the new AI features. We discussed implementing personalized recommendations and the team was very excited about the possibilities.',
                'memory_type': 'work',
                'importance': 8,
                'tags': ['work', 'meeting', 'ai', 'development']
            },
            {
                'content': 'Learned about machine learning algorithms today. The concept of neural networks is fascinating and I want to explore this further.',
                'memory_type': 'learning',
                'importance': 7,
                'tags': ['learning', 'machine-learning', 'neural-networks']
            },
            {
                'content': 'Spent time with family today. We went to the park and had a picnic. The kids were so happy playing on the swings.',
                'memory_type': 'personal',
                'importance': 9,
                'tags': ['family', 'park', 'picnic', 'kids']
            },
            {
                'content': 'Had an idea for a new mobile app that could help people track their daily habits. Need to research the market and create a prototype.',
                'memory_type': 'idea',
                'importance': 6,
                'tags': ['idea', 'mobile-app', 'habits', 'prototype']
            },
            {
                'content': 'Reminder to call the dentist tomorrow for my annual checkup. Also need to schedule the kids\' appointments.',
                'memory_type': 'reminder',
                'importance': 5,
                'tags': ['reminder', 'dentist', 'appointment', 'health']
            }
        ]
        
        for i, memory_data in enumerate(test_memories):
            # Create memory with different dates
            created_at = datetime.now() - timedelta(days=i*2)
            memory = Memory.objects.create(
                user=user,
                content=memory_data['content'],
                memory_type=memory_data['memory_type'],
                importance=memory_data['importance'],
                tags=memory_data['tags'],
                created_at=created_at
            )
            print(f"  ✅ Created memory {i+1}: {memory.content[:50]}...")
    
    # Test user patterns
    print("\n📊 Testing User Pattern Analysis...")
    patterns = service.get_user_memory_patterns(user)
    print(f"  Total memories: {patterns['total_memories']}")
    print(f"  Favorite types: {patterns['favorite_types']}")
    print(f"  Common tags: {patterns['common_tags'][:5]}")
    print(f"  Content themes: {patterns['content_themes'][:3]}")
    
    # Test personalized recommendations
    print("\n🎯 Testing Personalized Recommendations...")
    recommendations = service.get_personalized_recommendations(user)
    
    print("  Memory prompts:")
    for i, prompt in enumerate(recommendations['memory_prompts'][:3], 1):
        print(f"    {i}. {prompt}")
    
    print("  Content suggestions:")
    for suggestion in recommendations['content_suggestions'][:2]:
        print(f"    - {suggestion['title']}: {suggestion['description']}")
    
    print("  Improvement tips:")
    for tip in recommendations['improvement_tips'][:2]:
        print(f"    - {tip}")
    
    # Test memory insights
    print("\n💡 Testing Memory Insights...")
    insights = service.get_memory_insights(user)
    
    print("  Insights:")
    for insight in insights['insights'][:3]:
        print(f"    - {insight}")
    
    if insights['growth_metrics']:
        print("  Growth metrics:")
        for metric, value in insights['growth_metrics'].items():
            print(f"    - {metric}: {value}")
    
    # Test smart search suggestions
    print("\n🔍 Testing Smart Search Suggestions...")
    search_suggestions = service.get_smart_search_suggestions(user, "work meeting")
    print("  Search suggestions for 'work meeting':")
    for suggestion in search_suggestions[:3]:
        print(f"    - {suggestion}")
    
    # Test trending topics
    print("\n📈 Testing Trending Topics...")
    trending = recommendations['trending_topics']
    if trending:
        print("  Trending topics:")
        for topic in trending:
            print(f"    - {topic['tag']}: {topic['frequency']}x")
    else:
        print("  No trending topics found")
    
    # Test related memories
    print("\n🔗 Testing Related Memories...")
    related = recommendations['related_memories']
    if related:
        print("  Related memories:")
        for memory in related[:2]:
            print(f"    - {memory['content'][:50]}... ({memory['type']})")
    else:
        print("  No related memories found")
    
    print("\n✅ AI Recommendation Service Test Complete!")
    print("\nTo see these features in action:")
    print("1. Start the Django server: python manage.py runserver")
    print("2. Visit: http://127.0.0.1:8000/ai/dashboard/")
    print("3. Login with the test user credentials")

if __name__ == "__main__":
    test_ai_recommendations() 