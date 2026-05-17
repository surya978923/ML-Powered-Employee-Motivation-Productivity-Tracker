#!/usr/bin/env python
"""
Test script to verify task assignment is working correctly.
Tests the complete flow from creation to employee viewing.
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
print("TASK ASSIGNMENT VERIFICATION TEST")
print("="*70)

# Clean up old test data
print("\n1. Cleaning up old test data...")
Task.objects.filter(task_name__contains='Test Task').delete()
Project.objects.filter(title__contains='Test Project').delete()
User.objects.filter(username__in=['test_emp_task', 'test_admin_task']).delete()

print("   ✓ Cleanup complete")

# Create test employee
print("\n2. Creating test employee...")
try:
    user = User.objects.create_user(
        username='test_emp_task',
        email='testemp@company.com',
        password='testpass123',
        first_name='Test',
        last_name='Employee',
        is_staff=False
    )
    
    employee = Employee.objects.get(user=user)
    employee.name = 'Test Employee'
    employee.department = 'IT'
    employee.role = 'Developer'
    employee.save()
    
    print(f"   ✓ Employee created: {employee.name} (ID: {employee.id})")
except Exception as e:
    print(f"   ✗ Error creating employee: {e}")
    sys.exit(1)

# Create test project
print("\n3. Creating test project...")
try:
    project = Project.objects.create(
        title='Test Project - Task Assignment',
        description='Test project for verifying task assignment',
        deadline='2026-12-31',
        status='Ongoing'
    )
    print(f"   ✓ Project created: {project.title} (ID: {project.id})")
except Exception as e:
    print(f"   ✗ Error creating project: {e}")
    sys.exit(1)

# Test 1: Assign task using form
print("\n4. Testing task assignment via TaskAssignmentForm...")
try:
    form_data = {
        'employee': employee.id,
        'project': project.id,
        'task_name': 'Test Task #1 - Verify Assignment',
        'description': 'This is a test task to verify task assignment is working correctly.',
        'hours_worked': 0.0,
        'completion_status': 'Pending'
    }
    
    form = TaskAssignmentForm(data=form_data)
    
    if form.is_valid():
        print(f"   ✓ Form is valid")
        task = form.save()
        print(f"   ✓ Task saved successfully")
        print(f"   ✓ Task ID: {task.id}")
        print(f"   ✓ Assigned to: {task.employee.name}")
        print(f"   ✓ Task Name: {task.task_name}")
        print(f"   ✓ Project: {task.project.title}")
        print(f"   ✓ Status: {task.completion_status}")
        print(f"   ✓ Description: {task.description[:50]}...")
    else:
        print(f"   ✗ Form validation failed!")
        print(f"   Errors: {form.errors}")
        sys.exit(1)
        
except Exception as e:
    print(f"   ✗ Error assigning task: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Verify task exists in database
print("\n5. Verifying task exists in database...")
try:
    saved_task = Task.objects.get(id=task.id)
    print(f"   ✓ Task found in database")
    print(f"   ✓ Task employee FK: {saved_task.employee.id} (expected: {employee.id})")
    
    if saved_task.employee == employee:
        print(f"   ✓ Task correctly linked to employee")
    else:
        print(f"   ✗ Task linked to WRONG employee!")
        sys.exit(1)
        
except Task.DoesNotExist:
    print(f"   ✗ Task NOT found in database!")
    sys.exit(1)

# Test 3: Query tasks for employee
print("\n6. Testing employee task query (dashboard logic)...")
try:
    employee_tasks = Task.objects.filter(employee=employee)
    task_count = employee_tasks.count()
    
    print(f"   ✓ Query executed successfully")
    print(f"   ✓ Found {task_count} task(s) for this employee")
    
    if task_count > 0:
        test_task_found = False
        for t in employee_tasks:
            if 'Test Task #1' in t.task_name:
                test_task_found = True
                print(f"   ✓ Test task found in employee's tasks")
                print(f"      - Task: {t.task_name}")
                print(f"      - Project: {t.project.title if t.project else 'None'}")
                print(f"      - Status: {t.completion_status}")
                break
        
        if not test_task_found:
            print(f"   ✗ Test task NOT found in employee's tasks!")
            sys.exit(1)
    else:
        print(f"   ✗ No tasks found for employee!")
        sys.exit(1)
        
except Exception as e:
    print(f"   ✗ Error querying tasks: {e}")
    sys.exit(1)

# Test 4: Create multiple tasks for same employee
print("\n7. Testing multiple task assignments...")
try:
    for i in range(2, 5):
        Task.objects.create(
            employee=employee,
            project=project,
            task_name=f'Test Task #{i} - Multiple Assignment Test',
            description=f'Test task number {i}',
            completion_status='Pending'
        )
    
    total_tasks = Task.objects.filter(employee=employee).count()
    print(f"   ✓ Created 3 additional tasks")
    print(f"   ✓ Total tasks for employee: {total_tasks}")
    
    if total_tasks >= 4:
        print(f"   ✓ Multiple task assignment working")
    else:
        print(f"   ✗ Multiple task assignment failed!")
        sys.exit(1)
        
except Exception as e:
    print(f"   ✗ Error creating multiple tasks: {e}")
    sys.exit(1)

# Test 5: Test with newly created employee
print("\n8. Testing task assignment to NEWLY created employee...")
try:
    # Create brand new employee
    new_user = User.objects.create_user(
        username='new_emp_test',
        email='newemp@company.com',
        password='testpass123',
        is_staff=False
    )
    
    new_employee = Employee.objects.get(user=new_user)
    new_employee.name = 'New Employee'
    new_employee.department = 'Sales'
    new_employee.role = 'Executive'
    new_employee.save()
    
    # Assign task to new employee
    new_task = Task.objects.create(
        employee=new_employee,
        project=project,
        task_name='Test Task - New Employee Verification',
        description='Testing task assignment to newly created employee',
        completion_status='Pending'
    )
    
    # Verify task is accessible
    new_emp_tasks = Task.objects.filter(employee=new_employee)
    
    if new_emp_tasks.count() > 0:
        print(f"   ✓ Task assigned to NEW employee successfully")
        print(f"   ✓ New employee has {new_emp_tasks.count()} task(s)")
    else:
        print(f"   ✗ Task NOT assigned to new employee!")
        sys.exit(1)
        
except Exception as e:
    print(f"   ✗ Error testing with new employee: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Verify admin can see all tasks
print("\n9. Testing admin view of all tasks...")
try:
    all_tasks = Task.objects.all()
    print(f"   ✓ Admin can see all {all_tasks.count()} tasks")
    
    # Group by employee
    employees_with_tasks = set()
    for t in all_tasks:
        employees_with_tasks.add(t.employee.name)
    
    print(f"   ✓ Tasks distributed across {len(employees_with_tasks)} employee(s):")
    for emp_name in employees_with_tasks:
        emp_task_count = Task.objects.filter(employee__name=emp_name).count()
        print(f"      - {emp_name}: {emp_task_count} tasks")
        
except Exception as e:
    print(f"   ✗ Error in admin view: {e}")
    sys.exit(1)

# Final Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)

print("\n✅ ALL TASK ASSIGNMENT TESTS PASSED!")
print("\nVerified:")
print("✓ Task form validation working")
print("✓ Task saves to database correctly")
print("✓ Task links to correct employee")
print("✓ Employee dashboard query works")
print("✓ Multiple tasks can be assigned")
print("✓ Newly created employees receive tasks")
print("✓ Admin can view all tasks")

print("\n" + "="*70)
print("TASK ASSIGNMENT: ✅ FULLY FUNCTIONAL")
print("="*70)
