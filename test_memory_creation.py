#!/usr/bin/env python
"""
Test script to debug memory creation issues
"""
import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from django.contrib.auth.models import User
from memory_assistant.models import Memory
from memory_assistant.forms import MemoryForm

def test_memory_creation():
    """Test creating a memory programmatically"""
    print("=== Testing Memory Creation ===")
    
    # Get or create a test user
    try:
        user = User.objects.get(username='test_user')
        print(f"Using existing user: {user.username}")
    except User.DoesNotExist:
        # Check if any user exists
        user = User.objects.first()
        if user:
            print(f"Using first available user: {user.username}")
        else:
            print("No users found. Please create a user first.")
            return
    
    # Test direct model creation
    print("\n1. Testing direct model creation...")
    try:
        memory = Memory.objects.create(
            user=user,
            content="Test memory created programmatically",
            memory_type='general',
            importance=5,
            privacy_level='private',
            language='en'
        )
        print(f"✅ Direct creation successful! Memory ID: {memory.id}")
    except Exception as e:
        print(f"❌ Direct creation failed: {e}")
    
    # Test form validation
    print("\n2. Testing form validation...")
    form_data = {
        'content': 'Test memory created via form',
        'memory_type': 'general',
        'importance': 5,
        'privacy_level': 'private',
        'allow_comments': True,
        'allow_likes': True,
        'language': 'en'
    }
    
    form = MemoryForm(data=form_data)
    print(f"Form is valid: {form.is_valid()}")
    if not form.is_valid():
        print(f"Form errors: {form.errors}")
    else:
        try:
            memory = form.save(commit=False)
            memory.user = user
            memory.save()
            print(f"✅ Form creation successful! Memory ID: {memory.id}")
        except Exception as e:
            print(f"❌ Form save failed: {e}")
    
    # Check total memory count
    print(f"\n3. Total memories in database: {Memory.objects.count()}")
    print(f"Memories for user {user.username}: {Memory.objects.filter(user=user).count()}")

if __name__ == '__main__':
    test_memory_creation()

