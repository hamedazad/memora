#!/usr/bin/env python
"""
Test script for AI recommendation service
"""
import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append('C:\\memora_core')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from django.contrib.auth.models import User
from memory_assistant.recommendation_service import AIRecommendationService
from memory_assistant.models import Memory

def test_ai_recommendations():
    print("🧪 Testing AI Recommendation Service")
    print("=" * 50)
    
    # Initialize AI service
    ai_service = AIRecommendationService()
    print(f"🤖 AI Service Available: {ai_service.is_available()}")
    
    if not ai_service.is_available():
        print("❌ AI Service is not available. Checking OpenAI API key...")
        api_key = os.getenv('OPENAI_API_KEY')
        print(f"🔑 API Key exists: {bool(api_key)}")
        print(f"🔑 API Key valid format: {api_key and api_key != 'your_openai_api_key_here' and len(api_key) > 20}")
        return
    
    # Get a test user
    try:
        user = User.objects.first()
        if not user:
            print("❌ No users found in database")
            return
        
        print(f"👤 Testing with user: {user.username} (ID: {user.id})")
        
        # Check user's memories
        memories = Memory.objects.filter(user=user, is_archived=False)
        print(f"📚 User has {memories.count()} memories")
        
        if memories.exists():
            print("📝 Sample memories:")
            for i, memory in enumerate(memories[:3]):
                print(f"   {i+1}. {memory.content[:50]}...")
        
        # Test user patterns
        print("\n🔍 Testing user patterns...")
        patterns = ai_service.get_user_memory_patterns(user)
        print(f"📊 Patterns: {patterns}")
        
        # Test AI recommendations
        print("\n🤖 Testing AI recommendations...")
        recommendations = ai_service.get_personalized_recommendations(user)
        print(f"💡 Recommendations structure: {list(recommendations.keys())}")
        
        for key, value in recommendations.items():
            print(f"   {key}: {len(value) if isinstance(value, list) else 'N/A'} items")
            if isinstance(value, list) and value:
                print(f"      Sample: {value[0]}")
        
        # Test specific AI prompts generation
        print("\n🎯 Testing personalized prompts generation...")
        prompts = ai_service._generate_personalized_prompts(patterns)
        print(f"📝 Generated prompts: {prompts}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_recommendations()

