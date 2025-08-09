#!/usr/bin/env python3
"""
Script to create memory for calling Sergio's father next Monday
"""
import os
import sys
import django
from datetime import datetime

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from django.contrib.auth.models import User
from memory_assistant.models import Memory
from memory_assistant.services import ChatGPTService

def create_memory_for_sergio():
    """Create memory to call Sergio's father next Monday"""
    
    # Get or create a user (for demo purposes, we'll use the first user or create one)
    try:
        user = User.objects.first()
        if not user:
            print("No users found. Please create a user account first.")
            return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None
    
    print(f"Creating memory for user: {user.username}")
    
    # Memory content
    content = "remember to call Sergio's father next Monday"
    
    # Process with ChatGPT for auto-categorization and date parsing
    chatgpt_service = ChatGPTService()
    processed_data = chatgpt_service.process_memory(content)
    
    print(f"AI Processing Results:")
    print(f"- Summary: {processed_data.get('summary', '')}")
    print(f"- Memory Type: {processed_data.get('memory_type', 'general')}")
    print(f"- Importance: {processed_data.get('importance', 5)}")
    print(f"- Tags: {processed_data.get('tags', [])}")
    print(f"- Delivery Date: {processed_data.get('delivery_date')}")
    print(f"- Delivery Type: {processed_data.get('delivery_type', 'scheduled')}")
    
    # Create the memory
    memory = Memory(
        user=user,
        content=content,
        summary=processed_data.get('summary', ''),
        ai_reasoning=processed_data.get('reasoning', ''),
        tags=processed_data.get('tags', []),
        memory_type=processed_data.get('memory_type', 'general'),
        importance=processed_data.get('importance', 5)
    )
    
    # Apply date parsing results
    delivery_date = processed_data.get('delivery_date')
    if delivery_date and delivery_date != "None" and delivery_date is not None:
        # Handle both string and datetime objects
        if isinstance(delivery_date, str):
            try:
                from datetime import datetime
                memory.delivery_date = datetime.fromisoformat(delivery_date.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                # If parsing fails, don't set delivery_date
                pass
        else:
            memory.delivery_date = delivery_date
        memory.delivery_type = processed_data.get('delivery_type', 'scheduled')
    
    # Save the memory
    memory.save()
    
    print(f"\n✅ Memory created successfully!")
    print(f"   Memory ID: {memory.id}")
    print(f"   Content: {memory.content}")
    print(f"   Delivery Date: {memory.delivery_date}")
    print(f"   Memory Type: {memory.get_memory_type_display()}")
    print(f"   Importance: {memory.importance}")
    print(f"   Tags: {memory.tags}")
    
    return memory

if __name__ == "__main__":
    memory = create_memory_for_sergio()
    if memory:
        print("\n🎉 Success! The memory has been created and scheduled for next Monday.")
    else:
        print("\n❌ Failed to create memory.")
