#!/usr/bin/env python
"""
Test the AJAX endpoint for live status
"""

import os
import django
import sys
import json

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_project.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from tracker_app.models import Employee
from tracker_app.views import ajax_get_live_status

def test_ajax_endpoint():
    """Test the AJAX endpoint for live status"""
    
    print("=== TESTING AJAX ENDPOINT ===\n")
    
    # Create request factory
    factory = RequestFactory()
    
    # Test 1: Unauthenticated request
    print("1. Testing unauthenticated request...")
    try:
        request = factory.get('/ajax/get-live-status/')
        request.user = AnonymousUser()
        response = ajax_get_live_status(request)
        
        if response.status_code == 302:  # Redirect to login
            print("   ✓ Unauthenticated request properly redirected")
        else:
            print(f"   ✗ Expected redirect, got status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        return False
    
    # Test 2: Employee user request (should be forbidden)
    print("\n2. Testing employee user request...")
    try:
        # Create test employee user
        user = User.objects.create_user(
            username='ajax_test_employee',
            email='ajax_test@company.com',
            password='test123'
        )
        user.is_staff = False
        user.save()
        
        request = factory.get('/ajax/get-live-status/')
        request.user = user
        response = ajax_get_live_status(request)
        
        if response.status_code == 403:
            print("   ✓ Employee request properly forbidden")
        else:
            print(f"   ✗ Expected 403, got status {response.status_code}")
            return False
            
        user.delete()
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        return False
    
    # Test 3: Admin user request
    print("\n3. Testing admin user request...")
    try:
        # Create test admin user
        admin_user = User.objects.create_user(
            username='ajax_test_admin',
            email='ajax_admin@company.com',
            password='admin123'
        )
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        
        request = factory.get('/ajax/get-live-status/')
        request.user = admin_user
        response = ajax_get_live_status(request)
        
        if response.status_code == 200:
            data = json.loads(response.content)
            if 'employees' in data:
                print("   ✓ Admin request successful")
                print(f"   ✓ Returned {len(data['employees'])} employees")
            else:
                print("   ✗ Response missing 'employees' key")
                return False
        else:
            print(f"   ✗ Expected 200, got status {response.status_code}")
            return False
            
        admin_user.delete()
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        return False
    
    print("\n=== ALL AJAX TESTS PASSED ===")
    print("✅ AJAX endpoint properly handles authentication")
    print("✅ AJAX endpoint returns correct data structure")
    print("✅ AJAX endpoint properly restricts access")
    
    return True

if __name__ == '__main__':
    try:
        success = test_ajax_endpoint()
        if success:
            print("\n🎉 AJAX ENDPOINT IS WORKING CORRECTLY!")
        else:
            print("\n❌ AJAX ISSUES FOUND - NEEDS ATTENTION")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()