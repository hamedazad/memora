#!/usr/bin/env python3
"""
Local Development Setup Script for Memora Core
Run this script to set up your local development environment
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    if not os.path.exists('.env'):
        print("📝 Creating .env file from template...")
        if os.path.exists('env.example'):
            with open('env.example', 'r') as template:
                content = template.read()
            
            # Update for local development
            content = content.replace('APP_ENVIRONMENT=development', 'APP_ENVIRONMENT=local')
            content = content.replace('DEBUG=False', 'DEBUG=True')
            
            with open('.env', 'w') as env_file:
                env_file.write(content)
            print("✅ .env file created")
        else:
            print("❌ env.example not found")
            return False
    else:
        print("✅ .env file already exists")
    return True

def main():
    print("🚀 Setting up Memora Core for Local Development")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Create virtual environment
    if not os.path.exists('venv'):
        print("🐍 Creating virtual environment...")
        if not run_command('python -m venv venv', 'Creating virtual environment'):
            sys.exit(1)
    else:
        print("✅ Virtual environment already exists")
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        activate_cmd = 'venv\\Scripts\\activate'
        pip_cmd = 'venv\\Scripts\\pip'
    else:  # Unix/Linux/Mac
        activate_cmd = 'source venv/bin/activate'
        pip_cmd = 'venv/bin/pip'
    
    # Install requirements
    if not run_command(f'{pip_cmd} install -r requirements.txt', 'Installing Python dependencies'):
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Run database migrations
    if not run_command(f'{activate_cmd} && python manage.py migrate', 'Running database migrations'):
        sys.exit(1)
    
    # Collect static files
    if not run_command(f'{activate_cmd} && python manage.py collectstatic --noinput', 'Collecting static files'):
        sys.exit(1)
    
    # Create superuser if needed
    print("👤 Creating superuser (admin/admin123)...")
    create_superuser_cmd = f'{activate_cmd} && python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser(\'admin\', \'admin@example.com\', \'admin123\') if not User.objects.filter(username=\'admin\').exists() else print(\'Superuser already exists\')"'
    run_command(create_superuser_cmd, 'Creating superuser')
    
    print("\n🎉 Local setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys and settings")
    print("2. Run the development server:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
        print("   python manage.py runserver")
    else:
        print("   source venv/bin/activate")
        print("   python manage.py runserver")
    print("3. Open http://127.0.0.1:8000 in your browser")
    print("4. Login with admin/admin123")

if __name__ == '__main__':
    main()
