#!/usr/bin/env python3
"""
Check azadkhah user password
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from django.contrib.auth.models import User

def check_azadkhah():
    """Check azadkhah user"""
    try:
        azadkhah = User.objects.get(username='azadkhah')
        print(f"👤 Found user: {azadkhah.username} (ID: {azadkhah.id})")
        
        # Try different passwords
        passwords_to_try = ['Aa@123456', 'hamed123', 'azadkhah', 'password', '123456']
        
        for password in passwords_to_try:
            if azadkhah.check_password(password):
                print(f"✅ Correct password found: {password}")
                return password
        
        print("❌ None of the tested passwords work for azadkhah")
        return None
            
    except User.DoesNotExist:
        print("❌ User 'azadkhah' not found")
        return None

if __name__ == "__main__":
    check_azadkhah()
