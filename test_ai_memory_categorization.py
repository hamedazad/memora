#!/usr/bin/env python3
"""
Test script to demonstrate enhanced AI memory type recognition
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from memory_assistant.ai_services import get_ai_service
from memory_assistant.services import ChatGPTService

def test_memory_categorization():
    """Test the enhanced AI memory categorization with various types of memories"""
    
    print("🧠 Testing Enhanced AI Memory Type Recognition")
    print("=" * 60)
    
    # Test memories covering different categories
    test_memories = [
        {
            "content": "Meeting with the development team tomorrow at 2 PM to discuss the new feature implementation and project timeline.",
            "expected_type": "work"
        },
        {
            "content": "Need to buy groceries: milk, bread, eggs, and vegetables. Also pick up the dry cleaning.",
            "expected_type": "reminder"
        },
        {
            "content": "Had a great dinner with family tonight. We talked about our upcoming vacation plans and shared stories from our childhood.",
            "expected_type": "personal"
        },
        {
            "content": "Started learning Python programming today. Completed the basic syntax tutorial and built my first simple calculator program.",
            "expected_type": "learning"
        },
        {
            "content": "Got an idea for a new mobile app that helps people track their daily habits and build better routines.",
            "expected_type": "idea"
        },
        {
            "content": "Remember to call the dentist to schedule my annual checkup next week.",
            "expected_type": "reminder"
        },
        {
            "content": "Attended a workshop on machine learning fundamentals. Learned about neural networks and supervised learning algorithms.",
            "expected_type": "learning"
        },
        {
            "content": "Had a productive brainstorming session with the marketing team about our new product launch strategy.",
            "expected_type": "work"
        }
    ]
    
    try:
        # Test with enhanced AI service
        print("\n🔍 Testing Enhanced AI Service...")
        ai_service = get_ai_service()
        
        for i, test_memory in enumerate(test_memories, 1):
            print(f"\n📝 Test {i}: {test_memory['expected_type'].upper()} Memory")
            print(f"Content: {test_memory['content']}")
            
            try:
                result = ai_service.auto_categorize_memory(test_memory['content'])
                
                print(f"✅ AI Categorization:")
                print(f"   Category: {result.get('category', 'unknown')}")
                print(f"   Confidence: {result.get('confidence', 0)}%")
                print(f"   Importance: {result.get('importance', 5)}/10")
                print(f"   Tags: {', '.join(result.get('tags', []))}")
                print(f"   Summary: {result.get('summary', 'No summary')}")
                print(f"   Reasoning: {result.get('reasoning', 'No reasoning provided')}")
                
                # Check if categorization matches expected
                if result.get('category') == test_memory['expected_type']:
                    print(f"   🎯 CORRECT! Expected: {test_memory['expected_type']}")
                else:
                    print(f"   ❌ MISMATCH! Expected: {test_memory['expected_type']}, Got: {result.get('category')}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Test with ChatGPT service (fallback)
        print("\n\n🔍 Testing ChatGPT Service (Fallback)...")
        chatgpt_service = ChatGPTService()
        
        for i, test_memory in enumerate(test_memories[:3], 1):  # Test first 3
            print(f"\n📝 Test {i}: {test_memory['expected_type'].upper()} Memory")
            print(f"Content: {test_memory['content']}")
            
            try:
                result = chatgpt_service.process_memory(test_memory['content'])
                
                print(f"✅ ChatGPT Categorization:")
                print(f"   Category: {result.get('memory_type', 'unknown')}")
                print(f"   Importance: {result.get('importance', 5)}/10")
                print(f"   Tags: {', '.join(result.get('tags', []))}")
                print(f"   Summary: {result.get('summary', 'No summary')}")
                
                # Check if categorization matches expected
                if result.get('memory_type') == test_memory['expected_type']:
                    print(f"   🎯 CORRECT! Expected: {test_memory['expected_type']}")
                else:
                    print(f"   ❌ MISMATCH! Expected: {test_memory['expected_type']}, Got: {result.get('memory_type')}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n" + "=" * 60)
        print("✅ AI Memory Type Recognition Test Completed!")
        print("\nKey Features Demonstrated:")
        print("• Advanced AI categorization with confidence scores")
        print("• Detailed reasoning for categorization decisions")
        print("• Automatic tag generation")
        print("• Importance level assessment")
        print("• Fallback to ChatGPT service if enhanced AI fails")
        print("• Support for multiple memory types: work, personal, learning, idea, reminder, general")
        
    except Exception as e:
        print(f"❌ Error initializing AI service: {e}")
        print("Make sure your OpenAI API key is properly configured in the .env file.")

if __name__ == "__main__":
    test_memory_categorization() 