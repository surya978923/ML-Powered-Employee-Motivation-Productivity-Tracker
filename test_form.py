#!/usr/bin/env python
"""
Test the EmployeeCreationForm to ensure it works correctly with the signal
"""

import os
import django
import sys
from io import StringIO
from django.core.files.uploadedfile import SimpleUploadedFile

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_project.settings')
django.setup()

from django.contrib.auth.models import User
from tracker_app.models import Employee
from tracker_app.forms import EmployeeCreationForm

def test_employee_creation_form():
    """Test that the EmployeeCreationForm works correctly with signals"""
    
    print("=== TESTING EMPLOYEE CREATION FORM ===\n")
    
    # Clean up any existing test data
    User.objects.filter(username__startswith='form_test_').delete()
    
    # Test data
    form_data = {
        'username': 'form_test_employee_001',
        'password': 'testpassword123',
        'email': 'formtest001@company.com',
        'name': 'Form Test Employee',
        'department': 'IT Department',
        'role': 'Software Developer',
        'phone': '123-456-7890',
        'joining_date': '2024-01-15'
    }
    
    print("1. Testing form validation...")
    form = EmployeeCreationForm(data=form_data)
    if form.is_valid():
        print("   ✓ Form validation passed")
    else:
        print("   ✗ Form validation failed:")
        for field, errors in form.errors.items():
            print(f"     {field}: {errors}")
        return False
    
    print("\n2. Testing form save...")
    try:
        employee = form.save()
        print(f"   ✓ Form saved successfully")
        print(f"   ✓ Employee created: {employee.name}")
        print(f"   ✓ User created: {employee.user.username}")
        print(f"   ✓ Department: {employee.department}")
        print(f"   ✓ Role: {employee.role}")
        
        # Verify only one profile exists
        profile_count = Employee.objects.filter(user=employee.user).count()
        if profile_count == 1:
            print(f"   ✓ Only one profile exists for this user")
        else:
            print(f"   ✗ ERROR: Found {profile_count} profiles for one user!")
            return False
            
    except Exception as e:
        print(f"   ✗ ERROR saving form: {e}")
        return False
    
    print("\n3. Testing duplicate prevention...")
    # Try to create the same user again
    form2 = EmployeeCreationForm(data=form_data)
    if not form2.is_valid():
        if 'username' in form2.errors or 'email' in form2.errors:
            print("   ✓ Duplicate prevention working correctly")
        else:
            print("   ✗ Unexpected validation error")
            return False
    else:
        print("   ✗ Form should not be valid for duplicate data")
        return False
    
    print("\n=== ALL FORM TESTS PASSED ===")
    print("✅ EmployeeCreationForm works correctly with signals")
    print("✅ No duplicate profiles created")
    print("✅ Data integrity maintained")
    
    # Cleanup
    User.objects.filter(username__startswith='form_test_').delete()
    print("\n✓ Test data cleaned up")
    
    return True

if __name__ == '__main__':
    try:
        success = test_employee_creation_form()
        if success:
            print("\n🎉 FORM SYSTEM IS WORKING CORRECTLY!")
        else:
            print("\n❌ FORM ISSUES FOUND - NEEDS ATTENTION")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()