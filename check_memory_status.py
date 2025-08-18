#!/usr/bin/env python
"""Quick script to check memory categorization status"""

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

def check_status():
    print("Memory Database Status:")
    print("=" * 40)
    
    total = Memory.objects.count()
    print(f"Total memories: {total}")
    
    # Check for default/missing values
    general_type = Memory.objects.filter(memory_type='general').count()
    default_importance = Memory.objects.filter(importance=5).count()
    missing_summary = Memory.objects.filter(summary='').count()
    missing_tags = Memory.objects.filter(tags=[]).count()
    
    print(f"General type: {general_type}")
    print(f"Default importance (5): {default_importance}")
    print(f"Missing summary: {missing_summary}")
    print(f"Missing tags: {missing_tags}")
    
    # Find memories that definitely need updating
    needs_update = Memory.objects.filter(
        memory_type='general',
        importance=5,
        summary=''
    ).count()
    
    print(f"Memories needing update: {needs_update}")
    
    # Show memory type distribution
    print("\nMemory Type Distribution:")
    from django.db.models import Count
    types = Memory.objects.values('memory_type').annotate(count=Count('id')).order_by('-count')
    for t in types:
        print(f"  {t['memory_type']}: {t['count']}")

if __name__ == "__main__":
    check_status()
