#!/usr/bin/env python
"""
Migrate data from SQLite to PostgreSQL

This script helps you migrate your memora_core data from SQLite to PostgreSQL.

Usage:
    python migrate_sqlite_to_postgresql.py

Prerequisites:
    - PostgreSQL installed and running
    - Database and user created in PostgreSQL
    - Environment variables set for PostgreSQL connection
"""

import os
import sys
import django
from pathlib import Path

# Add project to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')


def migrate_to_postgresql():
    """
    Migrate from SQLite to PostgreSQL
    
    Steps:
    1. Verify SQLite database exists
    2. Export data from SQLite
    3. Verify PostgreSQL configuration
    4. Setup PostgreSQL database
    5. Import data to PostgreSQL
    6. Verify data integrity
    """
    
    print("=" * 70)
    print("  MEMORA CORE: SQLite → PostgreSQL Migration Tool")
    print("=" * 70)
    print()
    
    # Check if running in correct directory
    if not Path('manage.py').exists():
        print("❌ Error: Please run this script from the memora_core directory")
        print("   cd c:\\memora_core")
        print("   python migrate_sqlite_to_postgresql.py")
        return False
    
    # Step 1: Verify SQLite database
    print("Step 1: Verifying SQLite database...")
    sqlite_db = Path('db.sqlite3')
    
    if not sqlite_db.exists():
        print(f"❌ Error: {sqlite_db} not found")
        print()
        print("Options:")
        print("  1. If you haven't created it yet: python manage.py migrate")
        print("  2. If it's in a different location, move it here")
        return False
    
    size_mb = sqlite_db.stat().st_size / (1024 * 1024)
    print(f"✓ Found SQLite database: {sqlite_db}")
    print(f"  Size: {size_mb:.2f} MB")
    print()
    
    # Step 2: Export data from SQLite
    print("Step 2: Exporting data from SQLite...")
    backup_file = 'sqlite_backup.json'
    
    try:
        # Temporarily use SQLite
        os.environ['ENVIRONMENT'] = 'development'
        os.environ['DB_ENGINE'] = 'django.db.backends.sqlite3'
        
        # Initialize Django
        django.setup()
        
        from django.core.management import call_command
        from django.contrib.auth.models import User
        from memory_assistant.models import Memory, UserProfile
        
        # Check data before export
        user_count = User.objects.count()
        memory_count = Memory.objects.count()
        profile_count = UserProfile.objects.count()
        
        print(f"  Found:")
        print(f"    Users: {user_count}")
        print(f"    Memories: {memory_count}")
        print(f"    Profiles: {profile_count}")
        print()
        
        if user_count == 0:
            print("⚠️  Warning: No users found. Database might be empty.")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                return False
        
        # Export data
        print("  Exporting data...")
        with open(backup_file, 'w') as f:
            call_command(
                'dumpdata',
                '--natural-foreign',
                '--natural-primary',
                '--exclude', 'contenttypes',
                '--exclude', 'auth.Permission',
                '--indent', '2',
                stdout=f
            )
        
        backup_size_mb = Path(backup_file).stat().st_size / (1024 * 1024)
        print(f"✓ Data exported to {backup_file}")
        print(f"  Size: {backup_size_mb:.2f} MB")
        print()
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Make sure db.sqlite3 is not corrupted")
        print("  2. Try: python manage.py check")
        print("  3. Try: python manage.py dbshell")
        return False
    
    # Step 3: Verify PostgreSQL configuration
    print("Step 3: Verifying PostgreSQL configuration...")
    
    required_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print()
        print("Set these in your .env file or environment:")
        print()
        print("  DB_NAME=memora_db")
        print("  DB_USER=memora_user")
        print("  DB_PASSWORD=your_password")
        print("  DB_HOST=localhost")
        print("  DB_PORT=5432")
        print()
        return False
    
    print("✓ PostgreSQL configuration verified")
    print(f"  Host: {os.getenv('DB_HOST')}")
    print(f"  Database: {os.getenv('DB_NAME')}")
    print(f"  User: {os.getenv('DB_USER')}")
    print()
    
    # Step 4: Setup PostgreSQL database
    print("Step 4: Setting up PostgreSQL database...")
    
    try:
        # Switch to PostgreSQL
        os.environ['ENVIRONMENT'] = 'production'
        os.environ['DB_ENGINE'] = 'django.db.backends.postgresql'
        
        # Reload Django with new settings
        from importlib import reload
        import memora_project.settings
        reload(memora_project.settings)
        
        # Run migrations
        print("  Running migrations...")
        call_command('migrate', '--run-syncdb', verbosity=1)
        
        print("✓ PostgreSQL migrations complete")
        print()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Make sure PostgreSQL is running")
        print("  2. Verify database exists: createdb memora_db")
        print("  3. Test connection: psql -U memora_user -h localhost memora_db")
        return False
    
    # Step 5: Import data to PostgreSQL
    print("Step 5: Importing data to PostgreSQL...")
    
    try:
        print("  Loading data...")
        call_command('loaddata', backup_file, verbosity=1)
        
        print("✓ Data imported successfully")
        print()
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        print()
        print("You can try importing manually:")
        print(f"  python manage.py loaddata {backup_file}")
        print()
        print("Or check for errors:")
        print(f"  cat {backup_file} | python -m json.tool")
        return False
    
    # Step 6: Verify data integrity
    print("Step 6: Verifying data integrity...")
    
    try:
        from django.contrib.auth.models import User
        from memory_assistant.models import Memory, UserProfile
        
        new_user_count = User.objects.using('default').count()
        new_memory_count = Memory.objects.using('default').count()
        new_profile_count = UserProfile.objects.using('default').count()
        
        print("  PostgreSQL database now contains:")
        print(f"    Users: {new_user_count} (was {user_count})")
        print(f"    Memories: {new_memory_count} (was {memory_count})")
        print(f"    Profiles: {new_profile_count} (was {profile_count})")
        
        if new_user_count != user_count:
            print(f"  ⚠️  User count mismatch!")
        if new_memory_count != memory_count:
            print(f"  ⚠️  Memory count mismatch!")
        
        if new_user_count == user_count and new_memory_count == memory_count:
            print("  ✓ Data integrity verified")
        print()
        
    except Exception as e:
        print(f"⚠️  Warning: Could not verify data: {e}")
        print()
    
    # Success!
    print("=" * 70)
    print("✅ Migration Complete!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Test your application: python manage.py runserver")
    print("  2. Login and verify data is correct")
    print("  3. Update .env to use PostgreSQL permanently:")
    print("     ENVIRONMENT=production")
    print("     DB_ENGINE=django.db.backends.postgresql")
    print(f"  4. Keep backup safe: {backup_file}")
    print("  5. Optional: Remove db.sqlite3 (after verifying)")
    print()
    print("⚠️  If anything goes wrong, you can restore from backup:")
    print(f"     python manage.py loaddata {backup_file}")
    print()
    
    return True


if __name__ == '__main__':
    try:
        success = migrate_to_postgresql()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)




























