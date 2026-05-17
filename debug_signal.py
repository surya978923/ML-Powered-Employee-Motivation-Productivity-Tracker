#!/usr/bin/env python
"""
Debug script to understand the signal behavior
"""

import os
import django
import sys

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_project.settings')
django.setup()

from django.contrib.auth.models import User
from tracker_app.models import Employee

def debug_signal_behavior():
    """Debug the signal behavior step by step"""
    
    print("=== DEBUGGING SIGNAL BEHAVIOR ===\n")
    
    # Clean up first
    User.objects.filter(username__startswith='debug_').delete()
    
    print("1. Creating user with create_user()...")
    user = User.objects.create_user(
        username='debug_admin_001',
        email='debug@company.com',
        password='test123'
    )
    print(f"   After create_user: is_staff={user.is_staff}, is_superuser={user.is_superuser}")
    
    # Check if profile was created
    try:
        emp = Employee.objects.get(user=user)
        print(f"   ✓ Profile created during create_user(): {emp.name}")
    except Employee.DoesNotExist:
        print(f"   ✗ No profile created during create_user()")
    
    print("\n2. Setting is_staff=True and saving...")
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f"   After setting is_staff=True: is_staff={user.is_staff}, is_superuser={user.is_superuser}")
    
    # Check if another profile was created
    emp_count = Employee.objects.filter(user=user).count()
    print(f"   Total profiles for this user: {emp_count}")
    
    if emp_count > 1:
        print("   ❌ MULTIPLE PROFILES CREATED - THIS IS THE BUG!")
        employees = Employee.objects.filter(user=user)
        for i, emp in enumerate(employees):
            print(f"   Profile {i+1}: {emp.name}, {emp.department}")
    elif emp_count == 1:
        emp = Employee.objects.get(user=user)
        print(f"   ✓ Only one profile exists: {emp.name}")
    else:
        print("   ✗ No profiles exist")
    
    # Cleanup
    User.objects.filter(username__startswith='debug_').delete()
    print("\n✓ Debug data cleaned up")

if __name__ == '__main__':
    debug_signal_behavior()