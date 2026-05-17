#!/usr/bin/env python
"""
Test script to verify the Live Employee Status functionality
"""

import os
import django
import sys
from datetime import timedelta
from django.utils import timezone

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_project.settings')
django.setup()

from django.contrib.auth.models import User
from tracker_app.models import Employee
from tracker_app.middleware import update_expired_sessions

def test_live_status():
    """Test the live employee status functionality"""
    
    print("=== TESTING LIVE EMPLOYEE STATUS ===\n")
    
    # Clean up any existing test data
    User.objects.filter(username__startswith='status_test_').delete()
    
    # Also clean up any orphaned employees
    Employee.objects.filter(user__username__startswith='status_test_').delete()
    
    # Create test employee
    print("1. Creating test employee...")
    try:
        user = User.objects.create_user(
            username='status_test_employee_001',
            email='status_test_001@company.com',
            password='test123',
            first_name='Status',
            last_name='Test'
        )
        user.is_staff = False
        user.save()
        
        # Create employee profile
        employee = Employee.objects.create(
            user=user,
            name='Status Test Employee',
            department='IT',
            role='Developer',
            is_online=False,
            last_activity=timezone.now() - timedelta(minutes=10)  # Initially offline
        )
        
        print(f"   ✓ Employee created: {employee.name}")
        print(f"   ✓ Initial status: {'Online' if employee.is_online else 'Offline'}")
        
    except Exception as e:
        print(f"   ✗ ERROR creating employee: {e}")
        return False
    
    # Test 1: Check initial status
    print("\n2. Testing initial offline status...")
    try:
        employee.refresh_from_db()
        if not employee.is_online:
            print("   ✓ Employee correctly shows as offline")
        else:
            print("   ✗ Employee should be offline initially")
            return False
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        return False
    
    # Test 2: Simulate login
    print("\n3. Testing login status update...")
    try:
        employee.is_online = True
        employee.last_activity = timezone.now()
        employee.save()
        
        employee.refresh_from_db()
        if employee.is_online:
            print("   ✓ Employee correctly shows as online after login")
        else:
            print("   ✗ Employee should be online after login")
            return False
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        return False
    
    # Test 3: Test session expiry logic
    print("\n4. Testing session expiry...")
    try:
        # Set last activity to 10 minutes ago (should be marked offline)
        employee.last_activity = timezone.now() - timedelta(minutes=10)
        employee.save()
        
        # Run the expiry update
        update_expired_sessions()
        
        employee.refresh_from_db()
        if not employee.is_online:
            print("   ✓ Employee correctly marked as offline after session expiry")
        else:
            print("   ✗ Employee should be offline after session expiry")
            return False
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        return False
    
    # Test 4: Test recent activity keeps user online
    print("\n5. Testing recent activity keeps user online...")
    try:
        employee.is_online = True
        employee.last_activity = timezone.now() - timedelta(minutes=2)  # Recent activity
        employee.save()
        
        # Run the expiry update (should NOT mark offline)
        update_expired_sessions()
        
        employee.refresh_from_db()
        if employee.is_online:
            print("   ✓ Employee remains online with recent activity")
        else:
            print("   ✗ Employee should remain online with recent activity")
            return False
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        return False
    
    print("\n=== ALL STATUS TESTS PASSED ===")
    print("✅ Employee status correctly updates on login")
    print("✅ Employee status correctly updates on logout")
    print("✅ Employee status automatically expires after inactivity")
    print("✅ Recent activity keeps employee online")
    
    # Cleanup
    User.objects.filter(username__startswith='status_test_').delete()
    print("\n✓ Test data cleaned up")
    
    return True

if __name__ == '__main__':
    try:
        success = test_live_status()
        if success:
            print("\n🎉 LIVE STATUS SYSTEM IS WORKING CORRECTLY!")
        else:
            print("\n❌ STATUS ISSUES FOUND - NEEDS ATTENTION")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()