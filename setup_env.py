#!/usr/bin/env python3
"""
Helper script to set up environment variables for Memora
"""

import os
import secrets

def generate_secret_key():
    """Generate a secure Django secret key"""
    return ''.join([secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])

def create_env_file():
    """Create a .env file with required environment variables"""
    env_content = f"""# Memora Environment Variables
# Get your OpenAI API key from: https://platform.openai.com/api-keys

OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY={generate_secret_key()}
DEBUG=True
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
        print("\n📝 Next steps:")
        print("1. Edit the .env file and replace 'your_openai_api_key_here' with your actual OpenAI API key")
        print("2. Get your API key from: https://platform.openai.com/api-keys")
        print("3. Restart the Django server to load the new environment variables")
        print("\n⚠️  Note: The .env file contains sensitive information. Don't commit it to version control!")
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

if __name__ == "__main__":
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Operation cancelled.")
            exit()
    
    create_env_file() 