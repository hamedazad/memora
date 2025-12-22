#!/usr/bin/env python3
"""
Check memories in the database
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from django.contrib.auth.models import User
from memory_assistant.models import Memory

def check_memories():
    """Check what memories exist in the database"""
    print("🔍 Checking memories in database...")
    print("=" * 50)
    
    # Check users
    users = User.objects.all()
    print(f"👥 Found {users.count()} users:")
    for user in users:
        print(f"  - {user.username} (ID: {user.id}, Email: {user.email})")
    
    print("\n📚 Checking memories:")
    
    # Check all memories
    all_memories = Memory.objects.all()
    print(f"📚 Total memories: {all_memories.count()}")
    
    for memory in all_memories:
        print(f"  - ID: {memory.id}")
        print(f"    User: {memory.user.username}")
        print(f"    Title: {memory.title}")
        print(f"    Content: {memory.content[:100]}...")
        print(f"    Created: {memory.created_at}")
        print(f"    Archived: {memory.is_archived}")
        print()
    
    # Check memories for hamed user specifically
    try:
        hamed_user = User.objects.get(username='hamed')
        hamed_memories = Memory.objects.filter(user=hamed_user, is_archived=False)
        print(f"👤 Memories for 'hamed' user: {hamed_memories.count()}")
        
        for memory in hamed_memories:
            print(f"  - {memory.title}: {memory.content[:50]}...")
            
    except User.DoesNotExist:
        print("❌ User 'hamed' not found")

if __name__ == "__main__":
    check_memories()
