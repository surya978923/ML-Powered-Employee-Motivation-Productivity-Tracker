#!/usr/bin/env python
"""
Test script to simulate the actual employee login process.
This tests the exact flow that happens in the view.
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
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.messages import get_messages
from django.http import HttpRequest
from tracker_app.models import Employee

def simulate_login_view(username, password):
    """Simulate the employee_login_view function"""
    print(f"\n--- Simulating login for: {username} ---")
    
    # Create a mock request
    request = HttpRequest()
    request.method = 'POST'
    request.POST = {
        'username': username,
        'password': password
    }
    request.session = {}  # Mock session
    
    # Import the actual view function
    from tracker_app.views import employee_login_view
    
    try:
        # Call the view function
        response = employee_login_view(request)
        
        # Check if it's a redirect (successful login) or render (failed login)
        if hasattr(response, 'status_code') and response.status_code == 302:
            print("   ✓ Login successful - redirect response")
            return True
        else:
            print("   ✗ Login failed - form error or validation issue")
            # Try to get messages
            try:
                messages = list(get_messages(request))
                if messages:
                    print(f"   Messages: {[str(m) for m in messages]}")
            except:
                pass
            return False
            
    except Exception as e:
        print(f"   ✗ ERROR in view simulation: {e}")
        return False

def test_actual_login_flow():
    """Test the complete login flow"""
    
    print("=== Testing Actual Employee Login Flow ===\n")
    
    # Create test employee
    print("1. Creating test employee...")
    try:
        user = User.objects.create_user(
            username='flow_test_001',
            email='flow@test.com',
            password='flowpassword123',
            first_name='Flow',
            last_name='Tester'
        )
        user.is_staff = False
        user.save()
        
        print(f"   ✓ User created: {user.username}")
        
        # Verify employee profile exists
        employee = Employee.objects.get(user=user)
        print(f"   ✓ Employee profile: {employee.name}")
        
    except Exception as e:
        print(f"   ✗ ERROR creating test user: {e}")
        return False
    
    # Test 1: Correct credentials
    print("\n2. Testing correct credentials...")
    success1 = simulate_login_view('flow_test_001', 'flowpassword123')
    if success1:
        print("   ✓ Correct credentials work")
    else:
        print("   ✗ Correct credentials failed")
        return False
    
    # Test 2: Wrong password
    print("\n3. Testing wrong password...")
    success2 = simulate_login_view('flow_test_001', 'wrongpassword')
    if not success2:
        print("   ✓ Wrong password correctly rejected")
    else:
        print("   ✗ Wrong password was accepted (ERROR!)")
        return False
    
    # Test 3: Non-existent user
    print("\n4. Testing non-existent user...")
    success3 = simulate_login_view('nonexistent_user', 'password')
    if not success3:
        print("   ✓ Non-existent user correctly rejected")
    else:
        print("   ✗ Non-existent user was accepted (ERROR!)")
        return False
    
    # Test 4: Admin user (should be rejected)
    print("\n5. Testing admin user (should be rejected)...")
    try:
        admin_user = User.objects.create_user(
            username='admin_flow_test',
            email='admin@flow.com',
            password='adminpass123'
        )
        admin_user.is_staff = True
        admin_user.save()
        
        success4 = simulate_login_view('admin_flow_test', 'adminpass123')
        if not success4:
            print("   ✓ Admin user correctly rejected")
        else:
            print("   ✗ Admin user was accepted (ERROR!)")
            return False
            
    except Exception as e:
        print(f"   ✗ ERROR with admin test: {e}")
        return False
    
    print("\n=== All Flow Tests PASSED ===")
    print("✅ Complete login flow is working correctly")
    
    # Clean up
    print("\n=== Cleaning up test data ===")
    try:
        User.objects.filter(username__in=['flow_test_001', 'admin_flow_test']).delete()
        print("✓ Test data cleaned up")
    except Exception as e:
        print(f"⚠ Warning: Could not clean up test data: {e}")
    
    return True

if __name__ == '__main__':
    success = test_actual_login_flow()
    if success:
        print("\n🎉 All login flow tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some flow tests failed!")
        sys.exit(1)