#!/usr/bin/env python3
"""
Test script for Semantic Search functionality

This script demonstrates how to use the new semantic search service
to find memories by meaning rather than just keywords.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from memory_assistant.models import Memory, User
from memory_assistant.semantic_search_service import SemanticSearchService


def create_test_memories():
    """Create test memories for demonstration"""
    print("🔧 Creating test memories...")
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print("✅ Created test user")
    
    # Sample memories with different themes
    test_memories = [
        {
            'content': 'Had a great meeting with the development team today. We discussed the new AI features and everyone was excited about implementing semantic search.',
            'memory_type': 'work',
            'tags': ['meeting', 'development', 'AI', 'team'],
            'importance': 8
        },
        {
            'content': 'Learned about machine learning algorithms in my online course. The concept of embeddings and vector similarity is fascinating.',
            'memory_type': 'learning',
            'tags': ['machine learning', 'algorithms', 'embeddings', 'course'],
            'importance': 7
        },
        {
            'content': 'Had dinner with family tonight. Mom made her famous lasagna and we talked about upcoming vacation plans.',
            'memory_type': 'personal',
            'tags': ['family', 'dinner', 'vacation', 'mom'],
            'importance': 6
        },
        {
            'content': 'Got an idea for a new productivity app that uses AI to automatically categorize and organize user notes.',
            'memory_type': 'idea',
            'tags': ['productivity', 'app', 'AI', 'organization'],
            'importance': 9
        },
        {
            'content': 'Need to remember to call the dentist tomorrow to schedule my annual checkup.',
            'memory_type': 'reminder',
            'tags': ['dentist', 'appointment', 'health'],
            'importance': 5
        },
        {
            'content': 'Read an interesting article about natural language processing and how it can be used for better search functionality.',
            'memory_type': 'learning',
            'tags': ['NLP', 'search', 'article', 'technology'],
            'importance': 7
        },
        {
            'content': 'Team brainstorming session was productive. We came up with several innovative solutions for the user interface.',
            'memory_type': 'work',
            'tags': ['brainstorming', 'team', 'innovation', 'UI'],
            'importance': 8
        },
        {
            'content': 'Went for a long walk in the park and saw some beautiful flowers. It was a perfect day for photography.',
            'memory_type': 'personal',
            'tags': ['walk', 'park', 'flowers', 'photography'],
            'importance': 4
        }
    ]
    
    # Create memories
    created_count = 0
    for memory_data in test_memories:
        memory, created = Memory.objects.get_or_create(
            user=user,
            content=memory_data['content'],
            defaults={
                'memory_type': memory_data['memory_type'],
                'tags': memory_data['tags'],
                'importance': memory_data['importance'],
                'summary': f"Summary of {memory_data['memory_type']} memory",
                'ai_reasoning': f"AI categorized this as {memory_data['memory_type']} based on content analysis"
            }
        )
        if created:
            created_count += 1
    
    print(f"✅ Created {created_count} test memories")
    return user


def test_semantic_search():
    """Test the semantic search functionality"""
    print("\n🔍 Testing Semantic Search...")
    
    # Initialize semantic search service
    semantic_service = SemanticSearchService()
    
    if not semantic_service.is_available():
        print("❌ Semantic search service not available. Please check your OpenAI API key.")
        return
    
    print("✅ Semantic search service is available")
    
    # Get test user and their memories
    user = User.objects.get(username='testuser')
    memories = Memory.objects.filter(user=user, is_archived=False)
    
    print(f"📚 Found {memories.count()} memories to search through")
    
    # Test queries
    test_queries = [
        "artificial intelligence and machine learning",
        "family time and personal activities", 
        "work meetings and team collaboration",
        "health and medical appointments",
        "creative ideas and innovation",
        "outdoor activities and nature",
        "technology and software development"
    ]
    
    for query in test_queries:
        print(f"\n🔎 Testing query: '{query}'")
        print("-" * 50)
        
        # Test semantic search
        try:
            semantic_results = semantic_service.semantic_search(
                query, list(memories), top_k=3, similarity_threshold=0.3
            )
            
            if semantic_results:
                print(f"✅ Semantic search found {len(semantic_results)} results:")
                for memory, score in semantic_results:
                    print(f"  📝 [{score:.3f}] {memory.memory_type.upper()}: {memory.content[:80]}...")
            else:
                print("❌ No semantic search results found")
                
        except Exception as e:
            print(f"❌ Semantic search failed: {e}")
        
        # Test hybrid search
        try:
            hybrid_results = semantic_service.hybrid_search(
                query, list(memories), top_k=3
            )
            
            if hybrid_results:
                print(f"✅ Hybrid search found {len(hybrid_results)} results:")
                for memory, score in hybrid_results:
                    print(f"  📝 [{score:.3f}] {memory.memory_type.upper()}: {memory.content[:80]}...")
            else:
                print("❌ No hybrid search results found")
                
        except Exception as e:
            print(f"❌ Hybrid search failed: {e}")
    
    # Test search suggestions
    print(f"\n💡 Testing Search Suggestions...")
    print("-" * 50)
    
    try:
        suggestions = semantic_service.get_search_suggestions(
            "AI and technology", list(memories), top_k=5
        )
        
        if suggestions:
            print("✅ Search suggestions:")
            for suggestion in suggestions:
                print(f"  💭 {suggestion}")
        else:
            print("❌ No search suggestions generated")
            
    except Exception as e:
        print(f"❌ Search suggestions failed: {e}")
    
    # Test search intent analysis
    print(f"\n🧠 Testing Search Intent Analysis...")
    print("-" * 50)
    
    test_intent_queries = [
        "What meetings did I have today?",
        "Show me my work memories",
        "Find family activities",
        "When is my dentist appointment?"
    ]
    
    for query in test_intent_queries:
        try:
            intent = semantic_service.analyze_search_intent(query)
            print(f"🔍 Query: '{query}'")
            print(f"  📊 Intent: {intent}")
            
        except Exception as e:
            print(f"❌ Intent analysis failed for '{query}': {e}")


def test_similar_memories():
    """Test finding similar memories"""
    print(f"\n🔗 Testing Similar Memories...")
    print("-" * 50)
    
    semantic_service = SemanticSearchService()
    if not semantic_service.is_available():
        print("❌ Semantic search service not available")
        return
    
    user = User.objects.get(username='testuser')
    memories = Memory.objects.filter(user=user, is_archived=False)
    
    # Test finding similar memories for a specific memory
    test_memory = memories.filter(memory_type='work').first()
    if test_memory:
        print(f"🔍 Finding memories similar to: {test_memory.content[:60]}...")
        
        try:
            similar_memories = semantic_service.find_similar_memories(
                test_memory, list(memories), top_k=3, similarity_threshold=0.4
            )
            
            if similar_memories:
                print(f"✅ Found {len(similar_memories)} similar memories:")
                for memory, score in similar_memories:
                    print(f"  📝 [{score:.3f}] {memory.memory_type.upper()}: {memory.content[:80]}...")
            else:
                print("❌ No similar memories found")
                
        except Exception as e:
            print(f"❌ Similar memories search failed: {e}")


def main():
    """Main test function"""
    print("🚀 Semantic Search Test Suite")
    print("=" * 50)
    
    try:
        # Create test data
        create_test_memories()
        
        # Test semantic search
        test_semantic_search()
        
        # Test similar memories
        test_similar_memories()
        
        print("\n✅ All tests completed!")
        print("\n💡 To test in the web interface:")
        print("   1. Start the Django server: python manage.py runserver")
        print("   2. Go to http://localhost:8000")
        print("   3. Login with username: testuser, password: testpass123")
        print("   4. Try searching with queries like:")
        print("      - 'artificial intelligence'")
        print("      - 'family activities'")
        print("      - 'work meetings'")
        print("      - 'health appointments'")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
