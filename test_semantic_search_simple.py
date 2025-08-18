#!/usr/bin/env python3
"""
Simple Test script for Semantic Search functionality

This script tests the semantic search service without creating new memories.
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


def test_semantic_search_service():
    """Test the semantic search service with existing data"""
    print("🚀 Simple Semantic Search Test")
    print("=" * 50)
    
    # Initialize semantic search service
    semantic_service = SemanticSearchService()
    
    if not semantic_service.is_available():
        print("❌ Semantic search service not available. Please check your OpenAI API key.")
        print("💡 Make sure you have set OPENAI_API_KEY in your .env file")
        return
    
    print("✅ Semantic search service is available")
    
    # Get existing memories
    memories = Memory.objects.filter(is_archived=False)
    
    if not memories.exists():
        print("❌ No memories found in the database")
        print("💡 Please create some memories first through the web interface")
        return
    
    print(f"📚 Found {memories.count()} existing memories to search through")
    
    # Test queries
    test_queries = [
        "work and meetings",
        "personal activities", 
        "learning and education",
        "ideas and creativity",
        "reminders and tasks"
    ]
    
    for query in test_queries:
        print(f"\n🔎 Testing query: '{query}'")
        print("-" * 50)
        
        # Test semantic search
        try:
            semantic_results = semantic_service.semantic_search(
                query, list(memories), top_k=3, similarity_threshold=0.2
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
            "work and technology", list(memories), top_k=5
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
        "What meetings did I have?",
        "Show me my work memories",
        "Find personal activities",
        "When are my appointments?"
    ]
    
    for query in test_intent_queries:
        try:
            intent = semantic_service.analyze_search_intent(query)
            print(f"🔍 Query: '{query}'")
            print(f"  📊 Intent: {intent}")
            
        except Exception as e:
            print(f"❌ Intent analysis failed for '{query}': {e}")


def test_embedding_generation():
    """Test embedding generation functionality"""
    print(f"\n🔧 Testing Embedding Generation...")
    print("-" * 50)
    
    semantic_service = SemanticSearchService()
    if not semantic_service.is_available():
        print("❌ Semantic search service not available")
        return
    
    test_texts = [
        "This is a test memory about work and meetings",
        "Personal memory about family and friends",
        "Learning about artificial intelligence and machine learning"
    ]
    
    for text in test_texts:
        try:
            embedding = semantic_service.generate_embedding(text)
            if embedding:
                print(f"✅ Generated embedding for: '{text[:50]}...'")
                print(f"  📊 Embedding length: {len(embedding)} dimensions")
            else:
                print(f"❌ Failed to generate embedding for: '{text[:50]}...'")
        except Exception as e:
            print(f"❌ Embedding generation failed: {e}")


def test_similarity_calculation():
    """Test cosine similarity calculation"""
    print(f"\n📐 Testing Similarity Calculation...")
    print("-" * 50)
    
    semantic_service = SemanticSearchService()
    
    # Test with simple vectors
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [0.0, 1.0, 0.0]
    vec3 = [1.0, 0.0, 0.0]
    
    similarity1 = semantic_service.cosine_similarity(vec1, vec2)
    similarity2 = semantic_service.cosine_similarity(vec1, vec3)
    
    print(f"✅ Similarity between orthogonal vectors: {similarity1:.3f} (should be ~0)")
    print(f"✅ Similarity between identical vectors: {similarity2:.3f} (should be ~1)")


def main():
    """Main test function"""
    print("🚀 Simple Semantic Search Test Suite")
    print("=" * 50)
    
    try:
        # Test basic functionality
        test_similarity_calculation()
        
        # Test embedding generation
        test_embedding_generation()
        
        # Test semantic search with existing data
        test_semantic_search_service()
        
        print("\n✅ All tests completed!")
        print("\n💡 To test in the web interface:")
        print("   1. Start the Django server: python manage.py runserver")
        print("   2. Go to http://localhost:8000")
        print("   3. Login with your account")
        print("   4. Try searching with queries like:")
        print("      - 'work meetings'")
        print("      - 'personal activities'")
        print("      - 'learning and education'")
        print("      - 'ideas and creativity'")
        print("   5. Try different search types:")
        print("      - Hybrid (Recommended)")
        print("      - Semantic Only")
        print("      - Keyword Only")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
