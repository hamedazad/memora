#!/usr/bin/env python3
"""
Check memories for hamed user specifically
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from django.contrib.auth.models import User
from memory_assistant.models import Memory

def check_hamed_memories():
    """Check memories for hamed user"""
    print("🔍 Checking memories for hamed user...")
    print("=" * 50)
    
    try:
        hamed_user = User.objects.get(username='hamed')
        print(f"👤 Found user: {hamed_user.username} (ID: {hamed_user.id})")
        
        # Check all memories for hamed
        all_memories = Memory.objects.filter(user=hamed_user, is_archived=False)
        print(f"📚 Total memories for hamed: {all_memories.count()}")
        
        # Show recent memories
        recent_memories = all_memories.order_by('-created_at')[:5]
        print(f"\n📖 Recent 5 memories:")
        for i, memory in enumerate(recent_memories, 1):
            print(f"  {i}. ID: {memory.id}")
            print(f"     Content: {memory.content[:100]}...")
            print(f"     Type: {memory.memory_type}")
            print(f"     Created: {memory.created_at}")
            print()
            
        # Check if there are any memories at all
        if all_memories.count() == 0:
            print("❌ No memories found for hamed user!")
            print("💡 Creating a test memory...")
            
            # Create a test memory
            test_memory = Memory.objects.create(
                user=hamed_user,
                content="Test Memory for Hamed\n\nThis is a test memory to verify the mobile app can load memories for the hamed user.",
                memory_type='general',
                importance=8,
                tags=['test', 'hamed', 'mobile']
            )
            print(f"✅ Created test memory: {test_memory.id}")
            
    except User.DoesNotExist:
        print("❌ User 'hamed' not found!")
        print("Available users:")
        for user in User.objects.all():
            print(f"  - {user.username} (ID: {user.id})")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_hamed_memories()
