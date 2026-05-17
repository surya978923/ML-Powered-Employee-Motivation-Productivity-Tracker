#!/usr/bin/env python
"""
Test to reproduce the employee login issue.
This simulates exactly what happens when Admin creates an employee.
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

print("="*60)
print("REPRODUCING EMPLOYEE LOGIN ISSUE")
print("="*60)

# Simulate Admin creating a new employee
print("\n1. Creating employee via EmployeeCreationForm (Admin interface)...")

# Clean up any existing test user
User.objects.filter(username='TEST_EMP_2024').delete()

# Create form data (simulating admin filling the form)
form_data = {
    'username': 'TEST_EMP_2024',
    'password': 'testpass123',
    'email': 'testemp@company.com',
    'name': 'Test Employee 2024',
    'department': 'IT',
    'role': 'Developer',
}

print(f"   Form data:")
print(f"   - Username: {form_data['username']}")
print(f"   - Password: {form_data['password']}")
print(f"   - Email: {form_data['email']}")

# Create form and save
from django import forms
class TestEmployeeCreationForm(EmployeeCreationForm):
    # Make fields visible for testing
    joining_date = forms.DateField(required=False)
    phone = forms.CharField(required=False)
    profile_picture = forms.ImageField(required=False)

form = TestEmployeeCreationForm(data=form_data, files={})

if form.is_valid():
    print("   ✓ Form is valid")
    try:
        employee = form.save()
        print(f"   ✓ Form saved successfully")
        print(f"   ✓ Employee created: {employee.name}")
        print(f"   ✓ Employee ID: {employee.id}")
        print(f"   ✓ User: {employee.user.username}")
    except Exception as e:
        print(f"   ✗ Error saving form: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
else:
    print("   ✗ Form is NOT valid!")
    print(f"   Errors: {form.errors}")
    sys.exit(1)

# Check if User exists
print("\n2. Checking if User account exists...")
try:
    user = User.objects.get(username='TEST_EMP_2024')
    print(f"   ✓ User found: {user.username}")
    print(f"   ✓ Is staff: {user.is_staff}")
    print(f"   ✓ Is active: {user.is_active}")
    print(f"   ✓ Has usable password: {user.has_usable_password()}")
except User.DoesNotExist:
    print("   ✗ User does NOT exist!")
    sys.exit(1)

# Check if Employee profile exists
print("\n3. Checking if Employee profile exists...")
try:
    employee = Employee.objects.get(user__username='TEST_EMP_2024')
    print(f"   ✓ Employee profile found: {employee.name}")
    print(f"   ✓ Linked to User: {employee.user.username}")
except Employee.DoesNotExist:
    print("   ✗ Employee profile does NOT exist!")
    print("   ⚠ THIS IS THE PROBLEM - No Employee profile!")

# Try to authenticate
print("\n4. Testing authentication with credentials...")
auth_user = authenticate(username='TEST_EMP_2024', password='testpass123')

if auth_user:
    print(f"   ✓ Authentication SUCCESSFUL!")
    print(f"   ✓ Authenticated user: {auth_user.username}")
    print(f"   ✓ Is staff: {auth_user.is_staff}")
    
    # Check if authenticated user has employee profile
    try:
        emp_profile = Employee.objects.get(user=auth_user)
        print(f"   ✓ Has Employee profile: {emp_profile.name}")
    except Employee.DoesNotExist:
        print(f"   ⚠ WARNING: Authenticated user has NO Employee profile!")
        print(f"   ⚠ This will cause login view to fail!")
else:
    print(f"   ✗ Authentication FAILED!")
    print(f"   ✗ Invalid credentials even though user exists!")
    
    # Debug: Check password hash
    print("\n5. Debugging password hash...")
    user = User.objects.get(username='TEST_EMP_2024')
    print(f"   Password hash: {user.password[:20]}...")
    print(f"   Password algorithm: {user.password.split('$')[0] if '$' in user.password else 'UNKNOWN'}")
    
    # Try checking password directly
    if user.check_password('testpass123'):
        print(f"   ✓ user.check_password() returns TRUE")
    else:
        print(f"   ✗ user.check_password() returns FALSE")
        print(f"   ⚠ Password may not be hashed correctly!")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
