#!/usr/bin/env python3
"""
PostgreSQL Server Setup Script for Memora Core
This script helps set up PostgreSQL database for the Memora server
"""

import os
import sys
import subprocess
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def run_command(command, shell=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_postgresql_installed():
    """Check if PostgreSQL is installed"""
    success, stdout, stderr = run_command("psql --version")
    if success:
        print(f"✅ PostgreSQL is installed: {stdout.strip()}")
        return True
    else:
        print("❌ PostgreSQL is not installed or not in PATH")
        return False

def check_postgresql_running():
    """Check if PostgreSQL service is running"""
    # Windows
    success, stdout, stderr = run_command('sc query postgresql-x64-14')
    if success and "RUNNING" in stdout:
        print("✅ PostgreSQL service is running")
        return True
    
    # Try alternative service names
    for service in ['postgresql', 'postgres']:
        success, stdout, stderr = run_command(f'sc query {service}')
        if success and "RUNNING" in stdout:
            print(f"✅ PostgreSQL service ({service}) is running")
            return True
    
    print("❌ PostgreSQL service is not running")
    return False

def create_database_and_user():
    """Create database and user for Memora"""
    try:
        # Database configuration
        DB_NAME = 'memora_db'
        DB_USER = 'memora_user'
        DB_PASSWORD = 'memora_password_2024'
        
        # Connect to PostgreSQL as superuser (usually postgres)
        print("🔗 Connecting to PostgreSQL...")
        
        # Try to connect with different default credentials
        conn = None
        for user in ['postgres', 'postgresql']:
            try:
                conn = psycopg2.connect(
                    host='localhost',
                    port='5432',
                    user=user,
                    password='',  # Try without password first
                    database='postgres'
                )
                break
            except:
                try:
                    # Try with common passwords
                    for pwd in ['postgres', 'password', 'admin']:
                        conn = psycopg2.connect(
                            host='localhost',
                            port='5432',
                            user=user,
                            password=pwd,
                            database='postgres'
                        )
                        break
                    if conn:
                        break
                except:
                    continue
        
        if not conn:
            print("❌ Could not connect to PostgreSQL. Please ensure:")
            print("   1. PostgreSQL is installed and running")
            print("   2. You know the postgres user password")
            print("   3. PostgreSQL is accepting connections on localhost:5432")
            return False
        
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create user if not exists
        print(f"👤 Creating user '{DB_USER}'...")
        try:
            cursor.execute(
                sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                    sql.Identifier(DB_USER)
                ), [DB_PASSWORD]
            )
            print(f"✅ User '{DB_USER}' created successfully")
        except psycopg2.errors.DuplicateObject:
            print(f"ℹ️  User '{DB_USER}' already exists")
        
        # Create database if not exists
        print(f"🗄️  Creating database '{DB_NAME}'...")
        try:
            cursor.execute(
                sql.SQL("CREATE DATABASE {} OWNER {}").format(
                    sql.Identifier(DB_NAME),
                    sql.Identifier(DB_USER)
                )
            )
            print(f"✅ Database '{DB_NAME}' created successfully")
        except psycopg2.errors.DuplicateDatabase:
            print(f"ℹ️  Database '{DB_NAME}' already exists")
        
        # Grant privileges
        print(f"🔐 Granting privileges...")
        cursor.execute(
            sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                sql.Identifier(DB_NAME),
                sql.Identifier(DB_USER)
            )
        )
        
        cursor.close()
        conn.close()
        
        print("✅ Database setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def create_env_file():
    """Create .env file with PostgreSQL configuration"""
    env_content = f"""# Memora Core Server Environment Configuration
# PostgreSQL Database Settings
DB_ENGINE=django.db.backends.postgresql
DB_NAME=memora_db
DB_USER=memora_user
DB_PASSWORD=memora_password_2024
DB_HOST=localhost
DB_PORT=5432

# Django Settings
SECRET_KEY=django-insecure-change-this-in-production-{os.urandom(16).hex()}
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# CORS Settings for Mobile App
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8081,http://127.0.0.1:8081
CORS_ALLOW_CREDENTIALS=True

# API Settings
OPENAI_API_KEY=your-openai-api-key-here

# Server Settings
SERVER_MODE=development
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with PostgreSQL configuration")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def run_django_migrations():
    """Run Django migrations to set up the database schema"""
    print("🔄 Running Django migrations...")
    
    # Make migrations
    success, stdout, stderr = run_command("python manage.py makemigrations")
    if not success:
        print(f"❌ Failed to make migrations: {stderr}")
        return False
    
    # Run migrations
    success, stdout, stderr = run_command("python manage.py migrate")
    if success:
        print("✅ Django migrations completed successfully")
        return True
    else:
        print(f"❌ Failed to run migrations: {stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up PostgreSQL for Memora Core Server")
    print("=" * 50)
    
    # Check prerequisites
    if not check_postgresql_installed():
        print("\n📥 Please install PostgreSQL first:")
        print("   Windows: Download from https://www.postgresql.org/download/windows/")
        print("   Or use: winget install PostgreSQL.PostgreSQL")
        return
    
    if not check_postgresql_running():
        print("\n🔧 Please start PostgreSQL service:")
        print("   Windows: Run 'net start postgresql-x64-14' as administrator")
        print("   Or use Services.msc to start PostgreSQL service")
        return
    
    # Create database and user
    if not create_database_and_user():
        return
    
    # Create .env file
    if not create_env_file():
        return
    
    # Install psycopg2 if needed
    print("📦 Installing PostgreSQL adapter...")
    success, stdout, stderr = run_command("pip install psycopg2-binary")
    if success:
        print("✅ psycopg2-binary installed successfully")
    else:
        print("⚠️  Warning: Failed to install psycopg2-binary. Install manually if needed.")
    
    # Run migrations
    if not run_django_migrations():
        return
    
    print("\n🎉 PostgreSQL setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Update your .env file with correct OpenAI API key")
    print("   2. Run: python manage.py createsuperuser")
    print("   3. Run: python manage.py runserver 0.0.0.0:8000")
    print("   4. Your server will be accessible at http://localhost:8000")
    print("   5. API endpoints will be at http://localhost:8000/api/v1/")

if __name__ == "__main__":
    main()


