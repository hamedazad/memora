#!/usr/bin/env python3
"""
Create a test memory for hamed user
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from django.contrib.auth.models import User
from memory_assistant.models import Memory

def create_test_memory():
    """Create a test memory for hamed user"""
    print("📝 Creating test memory...")
    
    try:
        # Get hamed user
        hamed_user = User.objects.get(username='hamed')
        print(f"👤 Found user: {hamed_user.username}")
        
        # Create a test memory
        memory = Memory.objects.create(
            user=hamed_user,
            content="Test Memory Title\n\nThis is a test memory content to verify that the mobile app can load memories properly.",
            memory_type='general',
            importance=7,
            tags=['test', 'mobile', 'verification']
        )
        
        print(f"✅ Created memory: {memory.id}")
        print(f"   Content: {memory.content}")
        print(f"   Type: {memory.memory_type}")
        print(f"   Importance: {memory.importance}")
        
        # Check total memories for hamed
        total_memories = Memory.objects.filter(user=hamed_user, is_archived=False).count()
        print(f"📚 Total memories for hamed: {total_memories}")
        
    except User.DoesNotExist:
        print("❌ User 'hamed' not found")
    except Exception as e:
        print(f"❌ Error creating memory: {e}")

if __name__ == "__main__":
    create_test_memory()
