#!/usr/bin/env python3
"""
PostgreSQL Setup Script for Memora Memory Assistant
"""

import os
import subprocess
import sys
from pathlib import Path

def check_postgresql_installed():
    """Check if PostgreSQL is installed"""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PostgreSQL is installed")
            print(f"   Version: {result.stdout.strip()}")
            return True
        else:
            print("❌ PostgreSQL is not installed or not in PATH")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL is not installed or not in PATH")
        return False

def create_database_and_user():
    """Create database and user for Memora"""
    print("\n🔧 Setting up PostgreSQL database...")
    
    # Database configuration
    db_name = os.getenv('DB_NAME', 'memora_db')
    db_user = os.getenv('DB_USER', 'memora_user')
    db_password = os.getenv('DB_PASSWORD', 'memora_password')
    
    print(f"   Database: {db_name}")
    print(f"   User: {db_user}")
    print(f"   Host: {os.getenv('DB_HOST', 'localhost')}")
    print(f"   Port: {os.getenv('DB_PORT', '5432')}")
    
    # Create user
    try:
        subprocess.run([
            'psql', '-U', 'postgres', '-c', 
            f"CREATE USER {db_user} WITH PASSWORD '{db_password}';"
        ], check=True)
        print(f"✅ Created user: {db_user}")
    except subprocess.CalledProcessError:
        print(f"⚠️  User {db_user} might already exist")
    
    # Create database
    try:
        subprocess.run([
            'psql', '-U', 'postgres', '-c', 
            f"CREATE DATABASE {db_name} OWNER {db_user};"
        ], check=True)
        print(f"✅ Created database: {db_name}")
    except subprocess.CalledProcessError:
        print(f"⚠️  Database {db_name} might already exist")
    
    # Grant privileges
    try:
        subprocess.run([
            'psql', '-U', 'postgres', '-c', 
            f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};"
        ], check=True)
        print(f"✅ Granted privileges to {db_user}")
    except subprocess.CalledProcessError:
        print("⚠️  Could not grant privileges (database might already exist)")

def create_env_file():
    """Create .env file with database configuration"""
    env_file = Path('.env')
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        return
    
    env_content = f"""# Database Configuration
DB_NAME=memora_db
DB_USER=memora_user
DB_PASSWORD=memora_password
DB_HOST=localhost
DB_PORT=5432

# OpenAI API Key (add your key here)
OPENAI_API_KEY=your_openai_api_key_here

# Django Secret Key (will be generated)
DJANGO_SECRET_KEY=your_secret_key_here
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with database configuration")
    print("   Please update the .env file with your actual credentials")

def test_connection():
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        import psycopg2
        from dotenv import load_dotenv
        
        load_dotenv()
        
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME', 'memora_db'),
            user=os.getenv('DB_USER', 'memora_user'),
            password=os.getenv('DB_PASSWORD', 'memora_password'),
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432')
        )
        
        print("✅ Database connection successful!")
        conn.close()
        return True
        
    except ImportError:
        print("❌ psycopg2 not installed. Run: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 PostgreSQL Setup for Memora Memory Assistant")
    print("=" * 50)
    
    # Check if PostgreSQL is installed
    if not check_postgresql_installed():
        print("\n📋 To install PostgreSQL:")
        print("   Windows: Download from https://www.postgresql.org/download/windows/")
        print("   macOS: brew install postgresql")
        print("   Ubuntu: sudo apt-get install postgresql postgresql-contrib")
        return
    
    # Create .env file
    create_env_file()
    
    # Create database and user
    create_database_and_user()
    
    # Test connection
    if test_connection():
        print("\n🎉 PostgreSQL setup completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Update .env file with your actual credentials")
        print("   2. Run: python manage.py migrate")
        print("   3. Run: python manage.py createsuperuser")
        print("   4. Run: python manage.py runserver")
    else:
        print("\n❌ Setup incomplete. Please check the errors above.")

if __name__ == "__main__":
    main() 