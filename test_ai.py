#!/usr/bin/env python3
"""
Test script to check if AI features are working
"""

import os
import sys
import django
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from memory_assistant.services import ChatGPTService

def test_ai_service():
    """Test the ChatGPT service"""
    print("Testing AI Service...")
    print(f"API Key found: {bool(os.getenv('OPENAI_API_KEY'))}")
    print(f"API Key starts with: {os.getenv('OPENAI_API_KEY', 'NOT_FOUND')[:20]}...")
    
    # Test ChatGPTService
    service = ChatGPTService()
    print(f"AI Available: {service.is_available()}")
    
    if service.is_available():
        print("✅ AI Service is working!")
        
        # Test memory processing
        test_content = "I had a great meeting with the team today about the new project timeline."
        result = service.process_memory(test_content)
        print(f"Test memory processing result: {result}")
        
        return True
    else:
        print("❌ AI Service is not available")
        return False

if __name__ == "__main__":
    test_ai_service() 