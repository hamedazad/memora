#!/usr/bin/env python3
"""
Data Migration Script: SQLite to PostgreSQL
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from django.conf import settings
from django.db import connections
from memory_assistant.models import Memory
from django.contrib.auth.models import User
import json

def backup_sqlite_data():
    """Backup SQLite data to JSON files"""
    print("📦 Backing up SQLite data...")
    
    # Backup users
    users_data = []
    for user in User.objects.all():
        users_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'date_joined': user.date_joined.isoformat(),
        })
    
    with open('backup_users.json', 'w') as f:
        json.dump(users_data, f, indent=2)
    print(f"✅ Backed up {len(users_data)} users")
    
    # Backup memories
    memories_data = []
    for memory in Memory.objects.all():
        memories_data.append({
            'id': memory.id,
            'user_id': memory.user.id,
            'content': memory.content,
            'summary': memory.summary,
            'tags': memory.tags,
            'created_at': memory.created_at.isoformat(),
            'updated_at': memory.updated_at.isoformat(),
        })
    
    with open('backup_memories.json', 'w') as f:
        json.dump(memories_data, f, indent=2)
    print(f"✅ Backed up {len(memories_data)} memories")
    
    return users_data, memories_data

def switch_to_postgresql():
    """Switch Django settings to use PostgreSQL"""
    print("\n🔄 Switching to PostgreSQL...")
    
    # Temporarily change settings
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'memora_db'),
        'USER': os.getenv('DB_USER', 'memora_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'memora_password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
    
    # Close SQLite connection
    connections.close_all()
    
    print("✅ Switched to PostgreSQL configuration")

def restore_data_to_postgresql(users_data, memories_data):
    """Restore data to PostgreSQL"""
    print("\n📥 Restoring data to PostgreSQL...")
    
    # Restore users
    print("   Restoring users...")
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            id=user_data['id'],
            defaults={
                'username': user_data['username'],
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'is_staff': user_data['is_staff'],
                'is_superuser': user_data['is_superuser'],
                'date_joined': user_data['date_joined'],
            }
        )
        if created:
            print(f"     ✅ Created user: {user.username}")
        else:
            print(f"     ⚠️  User already exists: {user.username}")
    
    # Restore memories
    print("   Restoring memories...")
    for memory_data in memories_data:
        try:
            user = User.objects.get(id=memory_data['user_id'])
            memory, created = Memory.objects.get_or_create(
                id=memory_data['id'],
                defaults={
                    'user': user,
                    'content': memory_data['content'],
                    'summary': memory_data['summary'],
                    'tags': memory_data['tags'],
                    'created_at': memory_data['created_at'],
                    'updated_at': memory_data['updated_at'],
                }
            )
            if created:
                print(f"     ✅ Created memory: {memory.content[:50]}...")
            else:
                print(f"     ⚠️  Memory already exists: {memory.content[:50]}...")
        except User.DoesNotExist:
            print(f"     ❌ User not found for memory {memory_data['id']}")
    
    print("✅ Data restoration completed")

def verify_migration():
    """Verify that the migration was successful"""
    print("\n🔍 Verifying migration...")
    
    user_count = User.objects.count()
    memory_count = Memory.objects.count()
    
    print(f"   Users in PostgreSQL: {user_count}")
    print(f"   Memories in PostgreSQL: {memory_count}")
    
    if user_count > 0 and memory_count > 0:
        print("✅ Migration verification successful!")
        return True
    else:
        print("❌ Migration verification failed!")
        return False

def main():
    """Main migration function"""
    print("🚀 SQLite to PostgreSQL Migration")
    print("=" * 40)
    
    try:
        # Step 1: Backup SQLite data
        users_data, memories_data = backup_sqlite_data()
        
        # Step 2: Switch to PostgreSQL
        switch_to_postgresql()
        
        # Step 3: Restore data to PostgreSQL
        restore_data_to_postgresql(users_data, memories_data)
        
        # Step 4: Verify migration
        if verify_migration():
            print("\n🎉 Migration completed successfully!")
            print("\n📋 Next steps:")
            print("   1. Test your application")
            print("   2. Remove backup files if everything works")
            print("   3. Update your .env file with production credentials")
        else:
            print("\n❌ Migration failed. Please check the errors above.")
            
    except Exception as e:
        print(f"\n❌ Migration error: {e}")
        print("Please check your PostgreSQL setup and try again.")

if __name__ == "__main__":
    main() 