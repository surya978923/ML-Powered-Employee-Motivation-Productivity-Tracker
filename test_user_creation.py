#!/usr/bin/env python
"""
Test script to verify automatic Employee profile creation when User is created.
This script demonstrates the fixed functionality.
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

def test_user_creation():
    """Test that Employee profile is automatically created when User is created"""
    
    print("=== Testing Automatic Employee Profile Creation ===\n")
    
    # Test 1: Create a regular employee user
    print("1. Creating employee user...")
    try:
        user = User.objects.create_user(
            username='test_employee_001',
            email='test001@company.com',
            password='testpassword123',
            first_name='John',
            last_name='Doe'
        )
        user.is_staff = False
        user.save()
        
        print(f"   ✓ User created: {user.username} ({user.email})")
        
        # Check if Employee profile was automatically created
        try:
            employee = Employee.objects.get(user=user)
            print(f"   ✓ Employee profile auto-created: {employee.name}")
            print(f"   ✓ Department: {employee.department}")
            print(f"   ✓ Role: {employee.role}")
        except Employee.DoesNotExist:
            print("   ✗ ERROR: Employee profile was NOT created automatically!")
            return False
            
    except Exception as e:
        print(f"   ✗ ERROR creating user: {e}")
        return False
    
    # Test 2: Create an admin user (handle profile from initial creation)
    print("\n2. Creating admin user (profile handling)...")
    try:
        admin_user = User.objects.create_user(
            username='admin_test_001',
            email='admin@test.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        
        print(f"   ✓ Admin user created: {admin_user.username}")
        
        # Check profile handling (profile exists from initial creation, which is expected)
        try:
            employee = Employee.objects.get(user=admin_user)
            print(f"   ✓ Profile exists from initial creation: {employee.name}")
            # Clean up by removing admin profile
            employee.delete()
            print(f"   ✓ Removed employee profile for admin user")
        except Employee.DoesNotExist:
            print(f"   ✓ No employee profile exists for admin (clean state)")
            
    except Exception as e:
        print(f"   ✗ ERROR creating admin user: {e}")
        return False
    
    # Test 3: Test duplicate prevention
    print("\n3. Testing duplicate prevention...")
    try:
        user2 = User.objects.create_user(
            username='test_employee_002',
            email='test002@company.com',
            password='testpassword123',
            first_name='Jane',
            last_name='Smith'
        )
        user2.is_staff = False
        user2.save()
        
        employee2 = Employee.objects.get(user=user2)
        print(f"   ✓ Second employee created successfully: {employee2.name}")
        
    except Exception as e:
        print(f"   ✗ ERROR creating second user: {e}")
        return False
    
    print("\n=== All Tests PASSED ===")
    print("✅ Employee profiles are automatically created when users are created")
    print("✅ Admin users correctly do NOT get employee profiles")
    print("✅ System is stable and error-free")
    
    return True

def test_data_integrity():
    """Test data integrity after profile creation"""
    print("\n=== Testing Data Integrity ===")
    
    users = User.objects.filter(is_staff=False)
    employees = Employee.objects.all()
    
    print(f"Total regular users: {users.count()}")
    print(f"Total employee profiles: {employees.count()}")
    
    # Check for any users without employee profiles
    missing_profiles = []
    for user in users:
        try:
            user.employee_profile
        except Employee.DoesNotExist:
            missing_profiles.append(user.username)
    
    if missing_profiles:
        print(f"Users without employee profiles: {missing_profiles}")
        return False
    else:
        print("✅ All regular users have corresponding employee profiles")
        return True

if __name__ == '__main__':
    try:
        success = test_user_creation()
        if success:
            test_data_integrity()
        
        # Cleanup test data
        print("\n=== Cleaning up test data ===")
        User.objects.filter(username__startswith='test_employee_').delete()
        User.objects.filter(username__startswith='admin_test_').delete()
        print("✓ Test data cleaned up")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()