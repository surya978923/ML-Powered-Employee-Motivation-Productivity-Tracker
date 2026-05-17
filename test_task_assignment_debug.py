#!/usr/bin/env python
"""
Debug script to reproduce task assignment form errors.
Simulates exact admin workflow for assigning tasks.
"""

import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_project.settings')
django.setup()

from django.contrib.auth.models import User
from tracker_app.models import Employee, Task, Project
from tracker_app.forms import TaskAssignmentForm

print("="*70)
print("TASK ASSIGNMENT FORM DEBUG TEST")
print("="*70)

# Clean up old test data
print("\n1. Cleaning up test data...")
Task.objects.filter(task_name__contains='Debug Test').delete()
User.objects.filter(username__in=['debug_emp_001', 'debug_emp_002']).delete()

# Create test employees
print("\n2. Creating test employees...")
try:
    emp1_user = User.objects.create_user(
        username='debug_emp_001',
        email='emp1@company.com',
        password='testpass123',
        is_staff=False
    )
    emp1 = Employee.objects.get(user=emp1_user)
    emp1.name = 'Employee One'
    emp1.department = 'IT'
    emp1.role = 'Developer'
    emp1.save()
    print(f"   ✓ Created: {emp1.name} (ID: {emp1.id})")
    
    emp2_user = User.objects.create_user(
        username='debug_emp_002',
        email='emp2@company.com',
        password='testpass123',
        is_staff=False
    )
    emp2 = Employee.objects.get(user=emp2_user)
    emp2.name = 'Employee Two'
    emp2.department = 'HR'
    emp2.role = 'Manager'
    emp2.save()
    print(f"   ✓ Created: {emp2.name} (ID: {emp2.id})")
    
except Exception as e:
    print(f"   ✗ Error creating employees: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Create test project
print("\n3. Creating test project...")
try:
    project = Project.objects.create(
        title='Debug Test Project',
        description='Project for debugging task assignment',
        deadline='2026-12-31',
        status='Ongoing'
    )
    print(f"   ✓ Created project: {project.title} (ID: {project.id})")
except Exception as e:
    print(f"   ✗ Error creating project: {e}")
    sys.exit(1)

# Get list of employee IDs for form
employee_ids = list(Employee.objects.values_list('id', flat=True))
print(f"\n4. Available employees in database: {employee_ids}")

# Test 1: Valid form submission
print("\n5. Testing VALID form submission...")
form_data = {
    'employee': emp1.id,
    'project': project.id,
    'task_name': 'Debug Test Task #1',
    'description': 'This is a test task to debug form submission issues.',
    'hours_worked': 0.0,
    'completion_status': 'Pending'
}

print(f"   Form data:")
print(f"      - employee: {form_data['employee']}")
print(f"      - project: {form_data['project']}")
print(f"      - task_name: {form_data['task_name']}")
print(f"      - description: {form_data['description'][:40]}...")
print(f"      - hours_worked: {form_data['hours_worked']}")
print(f"      - completion_status: {form_data['completion_status']}")

form = TaskAssignmentForm(data=form_data)

if form.is_valid():
    print(f"   ✓ Form is VALID")
    try:
        task = form.save()
        print(f"   ✓ Task saved successfully")
        print(f"   ✓ Task ID: {task.id}")
        print(f"   ✓ Assigned to: {task.employee.name} (ID: {task.employee.id})")
        print(f"   ✓ Project: {task.project.title if task.project else 'None'}")
        
        # Verify in database
        saved_task = Task.objects.get(id=task.id)
        print(f"   ✓ Verified in database: {saved_task.task_name}")
        
    except Exception as e:
        print(f"   ✗ Error saving task: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"   ✗ Form is INVALID!")
    print(f"   Errors: {form.errors}")
    for field, errors in form.errors.items():
        print(f"      - {field}: {errors}")

# Test 2: Invalid form - missing required field
print("\n6. Testing INVALID form (missing required field)...")
invalid_form_data = {
    'employee': emp1.id,
    'project': project.id,
    'task_name': '',  # Empty task name - should fail
    'description': 'Test',
    'hours_worked': 0.0,
    'completion_status': 'Pending'
}

invalid_form = TaskAssignmentForm(data=invalid_form_data)
if not invalid_form.is_valid():
    print(f"   ✓ Correctly rejected invalid form")
    print(f"   Errors: {invalid_form.errors}")
else:
    print(f"   ⚠ Warning: Invalid form was accepted")

# Test 3: Test with different employee
print("\n7. Testing task assignment to second employee...")
form_data_2 = {
    'employee': emp2.id,
    'project': project.id,
    'task_name': 'Debug Test Task #2',
    'description': 'Testing assignment to different employee',
    'hours_worked': 1.5,
    'completion_status': 'In Progress'
}

form2 = TaskAssignmentForm(data=form_data_2)
if form2.is_valid():
    print(f"   ✓ Form is VALID for employee 2")
    task2 = form2.save()
    print(f"   ✓ Task assigned to: {task2.employee.name}")
    
    # Verify both employees have tasks
    emp1_tasks = Task.objects.filter(employee=emp1)
    emp2_tasks = Task.objects.filter(employee=emp2)
    print(f"   ✓ Employee 1 has {emp1_tasks.count()} task(s)")
    print(f"   ✓ Employee 2 has {emp2_tasks.count()} task(s)")
else:
    print(f"   ✗ Form INVALID for employee 2")
    print(f"   Errors: {form2.errors}")

# Test 4: Check form fields and widgets
print("\n8. Analyzing form structure...")
print(f"   Form fields:")
for field_name, field in form.fields.items():
    print(f"      - {field_name}: {field.__class__.__name__} (required={field.required})")

# Test 5: Check employee queryset
print("\n9. Checking employee queryset in form...")
employee_field = form.fields['employee']
print(f"   Employee field type: {employee_field.__class__.__name__}")
print(f"   Queryset: {employee_field.queryset}")
print(f"   Available employees:")
for emp in employee_field.queryset:
    print(f"      - {emp.name} (ID: {emp.id}, User: {emp.user.username})")

# Test 6: Test without project (optional field)
print("\n10. Testing task without project (optional)...")
form_data_no_project = {
    'employee': emp1.id,
    'project': '',  # Empty - should be allowed
    'task_name': 'Debug Test Task #3 - No Project',
    'description': 'Testing task without project association',
    'hours_worked': 0.0,
    'completion_status': 'Pending'
}

form_no_project = TaskAssignmentForm(data=form_data_no_project)
if form_no_project.is_valid():
    print(f"   ✓ Form is VALID without project")
    task_no_project = form_no_project.save()
    print(f"   ✓ Task saved: {task_no_project.task_name}")
    print(f"   ✓ Project: {task_no_project.project}")
else:
    print(f"   ✗ Form INVALID without project")
    print(f"   Errors: {form_no_project.errors}")

# Final Summary
print("\n" + "="*70)
print("DEBUG TEST SUMMARY")
print("="*70)

all_tasks = Task.objects.all()
print(f"\nTotal tasks in database: {all_tasks.count()}")
for task in all_tasks:
    print(f"   - {task.task_name} → {task.employee.name} ({task.completion_status})")

print("\n" + "="*70)
if form.is_valid() and form2.is_valid():
    print("✅ TASK ASSIGNMENT FORM IS WORKING CORRECTLY")
    print("="*70)
else:
    print("❌ TASK ASSIGNMENT FORM HAS ISSUES")
    print("="*70)
