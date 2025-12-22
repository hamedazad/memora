#!/usr/bin/env python3
"""
Check users and their authentication
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from django.contrib.auth.models import User

def check_users():
    """Check all users"""
    print("👥 Checking all users...")
    print("=" * 50)
    
    users = User.objects.all()
    for user in users:
        print(f"👤 User: {user.username}")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Is Active: {user.is_active}")
        print(f"   Is Staff: {user.is_staff}")
        print(f"   Has Password: {bool(user.password)}")
        print()
    
    # Test password for hamed
    try:
        hamed = User.objects.get(username='hamed')
        print(f"🔐 Testing password for hamed...")
        
        # Try different passwords
        passwords_to_try = ['hamed123', 'Aa@123456', 'hamed', 'password', '123456']
        
        for password in passwords_to_try:
            if hamed.check_password(password):
                print(f"✅ Correct password found: {password}")
                break
        else:
            print("❌ None of the tested passwords work for hamed")
            
    except User.DoesNotExist:
        print("❌ User 'hamed' not found")

if __name__ == "__main__":
    check_users()
