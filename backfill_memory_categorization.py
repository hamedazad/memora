#!/usr/bin/env python
"""
Backfill Memory Categorization Script

This script updates existing memories that may be missing proper AI categorization,
importance levels, or type assignments. It uses the enhanced AI service to analyze
and categorize memories that have default or missing values.
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from memory_assistant.models import Memory
from memory_assistant.ai_services import AIService
from django.db import transaction
from django.utils import timezone
import time

def backfill_memory_categorization():
    """Backfill existing memories with enhanced AI categorization."""
    
    print("🔍 Starting Memory Categorization Backfill...")
    print("=" * 60)
    
    # Initialize AI service
    try:
        ai_service = AIService()
        print("✅ AI Service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize AI service: {e}")
        return
    
    # Find memories that need categorization
    memories_to_update = Memory.objects.filter(
        # Memories with default or missing categorization
        memory_type='general',
        importance=5,
        # Or memories missing AI-generated fields
        summary='',
    ).order_by('created_at')
    
    total_memories = memories_to_update.count()
    
    if total_memories == 0:
        print("✅ No memories need categorization updates!")
        return
    
    print(f"📊 Found {total_memories} memories that need categorization")
    print(f"🤖 Starting AI analysis...\n")
    
    updated_count = 0
    failed_count = 0
    
    with transaction.atomic():
        for i, memory in enumerate(memories_to_update, 1):
            try:
                print(f"[{i}/{total_memories}] Processing memory {memory.id}: {memory.content[:50]}...")
                
                # Get AI categorization
                ai_result = ai_service.auto_categorize_memory(memory.content)
                
                # Track what was updated
                updates = []
                
                # Update memory type if it was general
                if memory.memory_type == 'general' and ai_result.get('category') != 'general':
                    old_type = memory.memory_type
                    memory.memory_type = ai_result.get('category', 'general')
                    updates.append(f"type: {old_type} → {memory.memory_type}")
                
                # Update importance if it was default
                if memory.importance == 5:
                    old_importance = memory.importance
                    memory.importance = ai_result.get('importance', 5)
                    if old_importance != memory.importance:
                        updates.append(f"importance: {old_importance} → {memory.importance}")
                
                # Always update AI-generated fields if missing
                if not memory.summary:
                    memory.summary = ai_result.get('summary', f"Memory: {memory.content[:100]}...")
                    updates.append("summary: added")
                
                if not memory.ai_reasoning:
                    memory.ai_reasoning = ai_result.get('reasoning', 'AI-generated categorization')
                    updates.append("reasoning: added")
                
                if not memory.tags:
                    memory.tags = ai_result.get('tags', ['general'])
                    updates.append(f"tags: added {len(memory.tags)} tags")
                
                # Handle scheduling if time-sensitive
                if ai_result.get('is_time_sensitive', False) and not memory.delivery_date:
                    try:
                        from memory_assistant.services import ChatGPTService
                        chatgpt_service = ChatGPTService()
                        if chatgpt_service.is_available():
                            delivery_date, _, _ = chatgpt_service.parse_date_references(memory.content)
                            if delivery_date:
                                memory.delivery_date = delivery_date
                                memory.delivery_type = ai_result.get('suggested_delivery_type', 'scheduled')
                                updates.append("scheduling: added")
                    except Exception:
                        pass  # Continue without scheduling if it fails
                
                # Save the memory
                memory.save()
                updated_count += 1
                
                if updates:
                    print(f"   ✅ Updated: {', '.join(updates)}")
                else:
                    print(f"   ℹ️  No changes needed")
                
                # Add small delay to avoid rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                failed_count += 1
                print(f"   ❌ Failed: {e}")
                continue
    
    print("\n" + "=" * 60)
    print(f"🎉 Backfill Complete!")
    print(f"✅ Successfully updated: {updated_count} memories")
    print(f"❌ Failed to update: {failed_count} memories")
    print(f"📊 Total processed: {updated_count + failed_count} memories")
    
    if updated_count > 0:
        print(f"\n🔍 Updated memories now have:")
        print(f"   • Proper memory types (work, personal, learning, etc.)")
        print(f"   • AI-calculated importance levels (1-10)")
        print(f"   • Generated summaries and tags")
        print(f"   • Time-sensitive scheduling where applicable")


def verify_categorization():
    """Verify the categorization results."""
    print("\n🔍 Verifying categorization results...")
    
    # Count memories by type
    type_counts = {}
    importance_counts = {}
    
    for memory in Memory.objects.all():
        # Count by type
        mem_type = memory.memory_type
        type_counts[mem_type] = type_counts.get(mem_type, 0) + 1
        
        # Count by importance
        importance = memory.importance
        importance_counts[importance] = importance_counts.get(importance, 0) + 1
    
    print(f"\n📊 Memory Types Distribution:")
    for mem_type, count in sorted(type_counts.items()):
        print(f"   {mem_type}: {count}")
    
    print(f"\n📊 Importance Distribution:")
    for importance in sorted(importance_counts.keys()):
        count = importance_counts[importance]
        print(f"   Level {importance}: {count}")
    
    # Check for memories missing fields
    missing_summary = Memory.objects.filter(summary='').count()
    missing_tags = Memory.objects.filter(tags=[]).count()
    default_type = Memory.objects.filter(memory_type='general').count()
    default_importance = Memory.objects.filter(importance=5).count()
    
    print(f"\n🔍 Remaining Default/Missing Values:")
    print(f"   Missing summary: {missing_summary}")
    print(f"   Missing tags: {missing_tags}")
    print(f"   General type: {default_type}")
    print(f"   Default importance (5): {default_importance}")


if __name__ == "__main__":
    print("🤖 Memory Categorization Backfill Tool")
    print("=====================================\n")
    
    # Run backfill
    backfill_memory_categorization()
    
    # Verify results
    verify_categorization()
    
    print(f"\n✨ All done! Your memories should now have proper categorization.")
