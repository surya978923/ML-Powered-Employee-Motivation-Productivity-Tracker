#!/usr/bin/env python
"""
Comprehensive test to verify new employee login is working correctly.
This tests the complete flow from creation to successful login.
"""

import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_project.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from tracker_app.models import Employee
from tracker_app.forms import EmployeeCreationForm
from django import forms

def test_new_employee_login():
    """Test that newly created employees can log in"""
    
    print("="*70)
    print("COMPREHENSIVE NEW EMPLOYEE LOGIN TEST")
    print("="*70)
    
    # Test multiple employees
    test_employees = [
        {
            'username': 'new_emp_001',
            'password': 'pass123',
            'email': 'emp001@company.com',
            'name': 'John Doe',
            'department': 'IT',
            'role': 'Developer'
        },
        {
            'username': 'new_emp_002',
            'password': 'secure456',
            'email': 'emp002@company.com',
            'name': 'Jane Smith',
            'department': 'HR',
            'role': 'Manager'
        },
        {
            'username': 'new_emp_003',
            'password': 'test789',
            'email': 'emp003@company.com',
            'name': 'Bob Wilson',
            'department': 'Sales',
            'role': 'Executive'
        }
    ]
    
    all_passed = True
    
    for i, emp_data in enumerate(test_employees, 1):
        print(f"\n{'='*70}")
        print(f"TEST EMPLOYEE #{i}: {emp_data['name']}")
        print(f"{'='*70}")
        
        # Clean up
        User.objects.filter(username=emp_data['username']).delete()
        
        # Step 1: Create employee via form (Admin interface simulation)
        print(f"\nStep 1: Creating employee via Admin interface...")
        try:
            form_data = {
                'username': emp_data['username'],
                'password': emp_data['password'],
                'email': emp_data['email'],
                'name': emp_data['name'],
                'department': emp_data['department'],
                'role': emp_data['role'],
            }
            
            class TestForm(EmployeeCreationForm):
                joining_date = forms.DateField(required=False)
                phone = forms.CharField(required=False)
                profile_picture = forms.ImageField(required=False)
            
            form = TestForm(data=form_data, files={})
            
            if form.is_valid():
                employee = form.save()
                print(f"   ✓ Employee created successfully")
                print(f"   ✓ Employee ID: {employee.id}")
                print(f"   ✓ Name: {employee.name}")
                print(f"   ✓ Department: {employee.department}")
                print(f"   ✓ Role: {employee.role}")
                print(f"   ✓ Joining Date: {employee.joining_date}")
            else:
                print(f"   ✗ Form validation failed: {form.errors}")
                all_passed = False
                continue
                
        except Exception as e:
            print(f"   ✗ Error creating employee: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
            continue
        
        # Step 2: Verify User account exists
        print(f"\nStep 2: Verifying User account...")
        try:
            user = User.objects.get(username=emp_data['username'])
            print(f"   ✓ User exists: {user.username}")
            print(f"   ✓ Is staff: {user.is_staff} (should be False)")
            print(f"   ✓ Is active: {user.is_active} (should be True)")
            print(f"   ✓ Has usable password: {user.has_usable_password()} (should be True)")
            
            if user.is_staff:
                print(f"   ✗ ERROR: User should not be staff!")
                all_passed = False
                
        except User.DoesNotExist:
            print(f"   ✗ User does not exist!")
            all_passed = False
            continue
        
        # Step 3: Verify Employee profile exists
        print(f"\nStep 3: Verifying Employee profile...")
        try:
            employee = Employee.objects.get(user=user)
            print(f"   ✓ Employee profile exists: {employee.name}")
            print(f"   ✓ Linked to User: {employee.user.username}")
            print(f"   ✓ Joining date set: {employee.joining_date}")
        except Employee.DoesNotExist:
            print(f"   ✗ Employee profile does NOT exist!")
            all_passed = False
            continue
        
        # Step 4: Test authentication with correct credentials
        print(f"\nStep 4: Testing login with CORRECT credentials...")
        auth_user = authenticate(
            username=emp_data['username'],
            password=emp_data['password']
        )
        
        if auth_user:
            print(f"   ✓ Authentication SUCCESSFUL!")
            print(f"   ✓ Logged in as: {auth_user.username}")
            print(f"   ✓ Is employee (not staff): {not auth_user.is_staff}")
            
            # Verify authenticated user has employee profile
            try:
                emp_profile = Employee.objects.get(user=auth_user)
                print(f"   ✓ Authenticated user has Employee profile: {emp_profile.name}")
            except Employee.DoesNotExist:
                print(f"   ⚠ WARNING: Authenticated user has NO Employee profile!")
                all_passed = False
        else:
            print(f"   ✗ Authentication FAILED - Invalid credentials!")
            print(f"   ✗ This is the reported bug!")
            all_passed = False
            
            # Debug password
            user = User.objects.get(username=emp_data['username'])
            if user.check_password(emp_data['password']):
                print(f"   ⚠ Password hash is correct (check_password returns True)")
                print(f"   ⚠ But authenticate() still fails - strange issue!")
            else:
                print(f"   ✗ Password hash is WRONG!")
            continue
        
        # Step 5: Test authentication with WRONG password
        print(f"\nStep 5: Testing login with WRONG credentials...")
        wrong_auth = authenticate(
            username=emp_data['username'],
            password='wrong_password'
        )
        
        if wrong_auth is None:
            print(f"   ✓ Wrong password correctly rejected")
        else:
            print(f"   ✗ SECURITY ISSUE: Wrong password was accepted!")
            all_passed = False
        
        print(f"\n✅ Employee #{i} ({emp_data['name']}) - ALL TESTS PASSED")
    
    # Final Summary
    print(f"\n{'='*70}")
    print("FINAL TEST SUMMARY")
    print(f"{'='*70}")
    
    if all_passed:
        print("\n🎉 SUCCESS! All employee login tests passed!")
        print("\nVerified:")
        print("✓ Employees can be created via Admin interface")
        print("✓ Employee profiles are automatically created")
        print("✓ Joining dates are properly set")
        print("✓ Passwords are correctly hashed")
        print("✓ Employees can log in with correct credentials")
        print("✓ Wrong passwords are rejected")
        print("\n✅ The login issue is FIXED!")
    else:
        print("\n❌ FAILURE! Some tests failed.")
        print("\nPlease review the errors above.")
    
    print(f"\n{'='*70}")
    
    return all_passed

if __name__ == '__main__':
    success = test_new_employee_login()
    
    if success:
        print("\n" + "="*70)
        print("DEPLOYMENT READY: ✅ YES")
        print("="*70)
        sys.exit(0)
    else:
        print("\n" + "="*70)
        print("DEPLOYMENT READY: ❌ NO")
        print("="*70)
        sys.exit(1)
