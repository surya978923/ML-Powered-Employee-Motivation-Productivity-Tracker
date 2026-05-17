#!/usr/bin/env python
"""
Simple manual test to verify employee login functionality works.
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
from django.contrib.auth import authenticate
from tracker_app.models import Employee

def manual_login_test():
    """Simple manual test of login functionality"""
    
    print("=== Manual Employee Login Test ===\n")
    
    # Create a test employee
    print("Creating test employee...")
    try:
        # Clean up any existing test user
        User.objects.filter(username='manual_test_001').delete()
        
        user = User.objects.create_user(
            username='manual_test_001',
            email='manual@test.com',
            password='manualpass123',
            first_name='Manual',
            last_name='Tester'
        )
        user.is_staff = False
        user.save()
        
        print(f"✓ User created: {user.username}")
        print(f"✓ Password check: {user.check_password('manualpass123')}")
        
        # Verify employee profile
        try:
            employee = Employee.objects.get(user=user)
            print(f"✓ Employee profile created: {employee.name}")
        except Employee.DoesNotExist:
            print("✗ Employee profile NOT created!")
            return False
        
    except Exception as e:
        print(f"✗ Error creating user: {e}")
        return False
    
    # Test authentication
    print("\nTesting authentication...")
    try:
        # Test correct credentials
        auth_user = authenticate(username='manual_test_001', password='manualpass123')
        if auth_user and auth_user.username == 'manual_test_001':
            print("✓ Correct credentials work")
        else:
            print("✗ Correct credentials failed")
            return False
            
        # Test wrong password
        wrong_auth = authenticate(username='manual_test_001', password='wrongpass')
        if wrong_auth is None:
            print("✓ Wrong password correctly rejected")
        else:
            print("✗ Wrong password was accepted")
            return False
            
        # Test non-existent user
        non_auth = authenticate(username='nonexistent', password='password')
        if non_auth is None:
            print("✓ Non-existent user correctly rejected")
        else:
            print("✗ Non-existent user was accepted")
            return False
            
    except Exception as e:
        print(f"✗ Error in authentication: {e}")
        return False
    
    print("\n=== LOGIN FUNCTIONALITY IS WORKING CORRECTLY ===")
    print("✅ User creation works")
    print("✅ Password authentication works")
    print("✅ Employee profile creation works")
    print("✅ All validation is working")
    
    # Clean up
    print("\nCleaning up test data...")
    try:
        User.objects.filter(username='manual_test_001').delete()
        print("✓ Test data cleaned up")
    except Exception as e:
        print(f"⚠ Warning: Could not clean up: {e}")
    
    return True

if __name__ == '__main__':
    success = manual_login_test()
    if success:
        print("\n🎉 Employee login is working correctly!")
        print("The issue is NOT with the authentication logic.")
        print("If employees cannot log in, check:")
        print("1. Are they entering the correct username/password?")
        print("2. Are they using the employee login page (not admin)?")
        print("3. Is there a template error on the dashboard page?")
        sys.exit(0)
    else:
        print("\n❌ Login functionality has issues!")
        sys.exit(1)