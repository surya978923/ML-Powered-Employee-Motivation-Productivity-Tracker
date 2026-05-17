#!/usr/bin/env python
"""
Test script using Django's test client to properly test the login flow.
This creates a realistic test environment.
"""

import os
import django
import sys

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from tracker_app.models import Employee

def test_with_django_client():
    """Test login using Django's test client"""
    
    print("=== Testing Employee Login with Django Test Client ===\n")
    
    # Create test client
    client = Client()
    
    # Create test employee
    print("1. Creating test employee...")
    try:
        user = User.objects.create_user(
            username='client_test_001',
            email='client@test.com',
            password='clientpassword123',
            first_name='Client',
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
    
    # Test 1: GET request to login page
    print("\n2. Testing GET request to login page...")
    try:
        response = client.get('/employee-login/')
        if response.status_code == 200:
            print("   ✓ Login page loads successfully")
        else:
            print(f"   ✗ Login page failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ ERROR loading login page: {e}")
        return False
    
    # Test 2: Correct login credentials
    print("\n3. Testing correct login credentials...")
    try:
        response = client.post('/employee-login/', {
            'username': 'client_test_001',
            'password': 'clientpassword123'
        })
        
        # Check if redirected (successful login)
        if response.status_code == 302:
            redirect_url = response.url
            print(f"   ✓ Login successful - redirected to: {redirect_url}")
            
            # Check if redirected to employee dashboard
            if 'employee/dashboard' in redirect_url or 'dashboard' in redirect_url:
                print("   ✓ Redirected to correct dashboard")
            else:
                print(f"   ⚠ Redirected to unexpected URL: {redirect_url}")
        else:
            print(f"   ✗ Login failed with status: {response.status_code}")
            print(f"   Response content: {response.content[:200]}")
            return False
            
    except Exception as e:
        print(f"   ✗ ERROR during login: {e}")
        return False
    
    # Test 3: Check if user is actually logged in
    print("\n4. Verifying user is logged in...")
    try:
        # Make a request to a protected page
        dashboard_response = client.get('/employee-dashboard/')
        if dashboard_response.status_code == 200:
            print("   ✓ User can access employee dashboard (logged in)")
        elif dashboard_response.status_code == 302:
            print("   ⚠ User redirected (might not be logged in properly)")
        else:
            print(f"   ✗ Unexpected response: {dashboard_response.status_code}")
    except Exception as e:
        print(f"   ✗ ERROR checking dashboard access: {e}")
    
    # Test 4: Wrong password
    print("\n5. Testing wrong password...")
    try:
        # Create new client to ensure clean state
        client2 = Client()
        response = client2.post('/employee-login/', {
            'username': 'client_test_001',
            'password': 'wrongpassword'
        })
        
        if response.status_code == 200:
            # Should render login page again with error
            if b'Invalid Employee ID or Password' in response.content:
                print("   ✓ Wrong password correctly rejected with error message")
            else:
                print("   ⚠ Wrong password rejected but no error message found")
        else:
            print(f"   ✗ Unexpected response for wrong password: {response.status_code}")
            
    except Exception as e:
        print(f"   ✗ ERROR testing wrong password: {e}")
    
    # Test 5: Admin user rejection
    print("\n6. Testing admin user rejection...")
    try:
        # Create admin user
        admin_user = User.objects.create_user(
            username='admin_client_test',
            email='admin@client.com',
            password='adminpass123'
        )
        admin_user.is_staff = True
        admin_user.save()
        
        client3 = Client()
        response = client3.post('/employee-login/', {
            'username': 'admin_client_test',
            'password': 'adminpass123'
        })
        
        if response.status_code == 200:
            # Should render login page with error message
            if b'Employee access required' in response.content:
                print("   ✓ Admin user correctly rejected with appropriate message")
            else:
                print("   ⚠ Admin user rejected but no proper error message")
        else:
            print(f"   ✗ Unexpected response for admin login: {response.status_code}")
            
    except Exception as e:
        print(f"   ✗ ERROR testing admin rejection: {e}")
    
    print("\n=== All Client Tests COMPLETED ===")
    
    # Clean up
    print("\n=== Cleaning up test data ===")
    try:
        User.objects.filter(username__in=['client_test_001', 'admin_client_test']).delete()
        print("✓ Test data cleaned up")
    except Exception as e:
        print(f"⚠ Warning: Could not clean up test data: {e}")
    
    return True

if __name__ == '__main__':
    success = test_with_django_client()
    if success:
        print("\n🎉 All client-based login tests completed!")
        sys.exit(0)
    else:
        print("\n❌ Some client tests failed!")
        sys.exit(1)