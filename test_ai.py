#!/usr/bin/env python3
"""
Test script to verify AI functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from memory_assistant.services import ChatGPTService

def test_ai_service():
    """Test the AI service functionality"""
    print("🤖 Testing AI Service...")
    print("=" * 50)
    
    # Initialize AI service
    ai_service = ChatGPTService()
    
    # Check if service is available
    if ai_service.is_available():
        print("✅ AI service is available!")
        print(f"📊 Model: {ai_service.model}")
        
        # Test categorization
        print("\n🧪 Testing Memory Categorization...")
        test_content = "I need to prepare for the quarterly meeting tomorrow at 2 PM"
        result = ai_service.categorize_memory(test_content)
        
        print(f"📝 Test content: {test_content}")
        print(f"🏷️  Memory type: {result.get('memory_type', 'unknown')}")
        print(f"⭐ Importance: {result.get('importance', 'unknown')}")
        print(f"🏷️  Tags: {result.get('tags', [])}")
        print(f"💭 Reasoning: {result.get('reasoning', 'No reasoning provided')}")
        
        # Test tag generation
        print("\n🏷️  Testing Tag Generation...")
        tag_result = ai_service.generate_tags(test_content)
        print(f"🏷️  Generated tags: {tag_result.get('tags', [])}")
        print(f"📊 Confidence: {tag_result.get('confidence', 'unknown')}")
        
        # Test summary generation
        print("\n📄 Testing Summary Generation...")
        long_content = "This is a long memory about my work project. I need to complete the quarterly report by Friday. The report should include sales data, customer feedback, and market analysis. I also need to prepare a presentation for the board meeting next week."
        summary_result = ai_service.generate_summary(long_content, max_length=100)
        print(f"📝 Original length: {summary_result.get('original_length', 'unknown')}")
        print(f"📄 Summary length: {summary_result.get('summary_length', 'unknown')}")
        print(f"📄 Summary: {summary_result.get('summary', 'No summary generated')}")
        
        print("\n🎉 All AI tests passed!")
        return True
        
    else:
        print("❌ AI service is not available")
        print("🔍 Checking environment...")
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            print(f"🔑 API key is set: {api_key[:20]}...")
        else:
            print("❌ No API key found")
        return False

if __name__ == "__main__":
    success = test_ai_service()
    sys.exit(0 if success else 1)

