#!/usr/bin/env python3
"""
Migration script from SQLite to PostgreSQL for Memora
This script helps migrate existing data from SQLite to PostgreSQL
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from django.core.management.commands.dumpdata import Command as DumpDataCommand
from django.core.management.commands.loaddata import Command as LoadDataCommand
from django.db import connection
import json

def backup_sqlite_data():
    """Backup data from SQLite database"""
    print("📦 Backing up SQLite data...")
    
    # Create backup directory
    backup_dir = 'sqlite_backup'
    os.makedirs(backup_dir, exist_ok=True)
    
    # Dump data from SQLite
    apps_to_backup = [
        'memory_assistant.Memory',
        'memory_assistant.UserProfile', 
        'memory_assistant.SharedMemory',
        'memory_assistant.MemoryLike',
        'memory_assistant.MemoryComment',
        'auth.User',
    ]
    
    for app_model in apps_to_backup:
        try:
            output_file = os.path.join(backup_dir, f'{app_model.replace(".", "_")}.json')
            execute_from_command_line([
                'manage.py', 'dumpdata', app_model, 
                '--indent', '2', '--output', output_file
            ])
            print(f"✅ Backed up {app_model}")
        except Exception as e:
            print(f"⚠️  Warning: Could not backup {app_model}: {e}")
    
    print(f"✅ Data backed up to {backup_dir}/")
    return backup_dir

def setup_postgresql():
    """Setup PostgreSQL database"""
    print("🗄️  Setting up PostgreSQL...")
    
    # Update environment to use PostgreSQL
    os.environ['DB_ENGINE'] = 'django.db.backends.postgresql'
    os.environ['DB_NAME'] = 'memora_db'
    os.environ['DB_USER'] = 'memora_user'
    os.environ['DB_PASSWORD'] = 'memora_password_2024'
    os.environ['DB_HOST'] = 'localhost'
    os.environ['DB_PORT'] = '5432'
    
    # Run migrations
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ PostgreSQL migrations completed")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def restore_data(backup_dir):
    """Restore data to PostgreSQL"""
    print("📥 Restoring data to PostgreSQL...")
    
    # Load data in correct order (to handle foreign keys)
    load_order = [
        'auth_User.json',
        'memory_assistant_UserProfile.json',
        'memory_assistant_Memory.json',
        'memory_assistant_SharedMemory.json',
        'memory_assistant_MemoryLike.json',
        'memory_assistant_MemoryComment.json',
    ]
    
    for filename in load_order:
        filepath = os.path.join(backup_dir, filename)
        if os.path.exists(filepath):
            try:
                execute_from_command_line(['manage.py', 'loaddata', filepath])
                print(f"✅ Loaded {filename}")
            except Exception as e:
                print(f"⚠️  Warning: Could not load {filename}: {e}")
        else:
            print(f"ℹ️  Skipping {filename} (file not found)")
    
    print("✅ Data restoration completed")

def verify_migration():
    """Verify the migration was successful"""
    print("🔍 Verifying migration...")
    
    try:
        from memory_assistant.models import Memory, UserProfile
        from django.contrib.auth.models import User
        
        user_count = User.objects.count()
        memory_count = Memory.objects.count()
        profile_count = UserProfile.objects.count()
        
        print(f"✅ Migration verified:")
        print(f"   • Users: {user_count}")
        print(f"   • Memories: {memory_count}")
        print(f"   • Profiles: {profile_count}")
        
        return True
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def create_env_file():
    """Create .env file for PostgreSQL"""
    env_content = """# Memora Core - PostgreSQL Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=memora_db
DB_USER=memora_user
DB_PASSWORD=memora_password_2024
DB_HOST=localhost
DB_PORT=5432

# Django Settings
SECRET_KEY=django-insecure-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# CORS Settings for Mobile App
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8081,http://127.0.0.1:8081
CORS_ALLOW_CREDENTIALS=True

# API Settings
OPENAI_API_KEY=your-openai-api-key-here
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    print("✅ Created .env file for PostgreSQL")

def main():
    """Main migration function"""
    print("🔄 Migrating Memora from SQLite to PostgreSQL")
    print("=" * 50)
    
    # Check if SQLite database exists
    if not os.path.exists('db.sqlite3'):
        print("ℹ️  No SQLite database found. Setting up fresh PostgreSQL installation...")
        create_env_file()
        if setup_postgresql():
            print("✅ Fresh PostgreSQL setup completed!")
        return
    
    print("📋 Migration steps:")
    print("   1. Backup SQLite data")
    print("   2. Setup PostgreSQL")
    print("   3. Restore data to PostgreSQL")
    print("   4. Verify migration")
    
    response = input("\nContinue with migration? (y/N): ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        return
    
    # Step 1: Backup SQLite data
    backup_dir = backup_sqlite_data()
    
    # Step 2: Create .env file
    create_env_file()
    
    # Step 3: Setup PostgreSQL
    if not setup_postgresql():
        print("❌ PostgreSQL setup failed. Check your PostgreSQL installation.")
        return
    
    # Step 4: Restore data
    restore_data(backup_dir)
    
    # Step 5: Verify migration
    if verify_migration():
        print("\n🎉 Migration completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Test your application: python manage.py runserver")
        print("   2. Create new superuser if needed: python manage.py createsuperuser")
        print("   3. Backup SQLite file: mv db.sqlite3 db.sqlite3.backup")
        print("   4. Update mobile app to use new server API")
    else:
        print("❌ Migration verification failed. Please check the logs.")

if __name__ == "__main__":
    main()