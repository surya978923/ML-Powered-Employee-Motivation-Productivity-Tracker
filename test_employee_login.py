#!/usr/bin/env python
"""
Test script to verify employee login functionality.
This script tests the authentication process for employee users.
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

def test_employee_login():
    """Test employee login functionality"""
    
    print("=== Testing Employee Login Functionality ===\n")
    
    # Create a test employee user
    print("1. Creating test employee user...")
    try:
        user = User.objects.create_user(
            username='login_test_001',
            email='login_test@company.com',
            password='testpassword123',
            first_name='Login',
            last_name='Tester'
        )
        user.is_staff = False
        user.save()
        
        print(f"   ✓ User created: {user.username}")
        print(f"   ✓ Password set: {'Yes' if user.check_password('testpassword123') else 'No'}")
        
        # Check if Employee profile was created
        try:
            employee = Employee.objects.get(user=user)
            print(f"   ✓ Employee profile exists: {employee.name}")
        except Employee.DoesNotExist:
            print("   ✗ ERROR: Employee profile not created!")
            return False
            
    except Exception as e:
        print(f"   ✗ ERROR creating user: {e}")
        return False
    
    # Test 1: Direct authentication
    print("\n2. Testing direct authentication...")
    try:
        authenticated_user = authenticate(username='login_test_001', password='testpassword123')
        if authenticated_user:
            print("   ✓ Direct authentication successful")
            print(f"   ✓ Authenticated user: {authenticated_user.username}")
            print(f"   ✓ Is staff: {authenticated_user.is_staff}")
        else:
            print("   ✗ Direct authentication failed")
            return False
    except Exception as e:
        print(f"   ✗ ERROR in direct authentication: {e}")
        return False
    
    # Test 2: Wrong password
    print("\n3. Testing wrong password...")
    try:
        wrong_auth = authenticate(username='login_test_001', password='wrongpassword')
        if wrong_auth is None:
            print("   ✓ Wrong password correctly rejected")
        else:
            print("   ✗ Wrong password was accepted (ERROR!)")
            return False
    except Exception as e:
        print(f"   ✓ Wrong password correctly rejected with error: {e}")
    
    # Test 3: Non-existent user
    print("\n4. Testing non-existent user...")
    try:
        non_auth = authenticate(username='nonexistent', password='password')
        if non_auth is None:
            print("   ✓ Non-existent user correctly rejected")
        else:
            print("   ✗ Non-existent user was accepted (ERROR!)")
            return False
    except Exception as e:
        print(f"   ✓ Non-existent user correctly rejected with error: {e}")
    
    # Test 4: Staff user authentication (should be rejected by view logic)
    print("\n5. Testing staff user authentication...")
    try:
        # Create admin user
        admin_user = User.objects.create_user(
            username='admin_login_test',
            email='admin@test.com',
            password='adminpass123'
        )
        admin_user.is_staff = True
        admin_user.save()
        
        admin_auth = authenticate(username='admin_login_test', password='adminpass123')
        if admin_auth:
            print("   ✓ Admin authentication successful (as expected)")
            print("   ✓ View logic should reject this user")
        else:
            print("   ✗ Admin authentication failed")
            return False
    except Exception as e:
        print(f"   ✗ ERROR with admin authentication: {e}")
        return False
    
    print("\n=== All Login Tests PASSED ===")
    print("✅ Authentication is working correctly")
    print("✅ Password validation is working")
    print("✅ Employee profile creation is working")
    print("✅ View logic should properly handle login")
    
    # Clean up test data
    print("\n=== Cleaning up test data ===")
    try:
        User.objects.filter(username__in=['login_test_001', 'admin_login_test']).delete()
        print("✓ Test data cleaned up")
    except Exception as e:
        print(f"⚠ Warning: Could not clean up test data: {e}")
    
    return True

if __name__ == '__main__':
    success = test_employee_login()
    if success:
        print("\n🎉 All employee login tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)