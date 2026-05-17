#!/usr/bin/env python
"""
Test script to verify the three critical fixes:
1. New Employee Login
2. Task Assignment for New Employees  
3. AI Productivity Clustering (K-Means)
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
from django.contrib.auth import authenticate
from tracker_app.models import Employee, Task, Attendance, Productivity
from tracker_app.ml_model import calculate_productivity_scores

def test_employee_creation_and_login():
    """Test Issue #1: New Employee Login"""
    print("\n" + "="*60)
    print("TEST 1: New Employee Creation and Login")
    print("="*60)
    
    # Clean up any existing test users
    User.objects.filter(username='test_new_employee_001').delete()
    
    # Simulate employee creation by admin
    print("\n1. Creating new employee via Admin interface...")
    try:
        user = User.objects.create_user(
            username='test_new_employee_001',
            email='test001@company.com',
            password='secure_password_123',
            first_name='Test',
            last_name='Employee',
            is_staff=False
        )
        
        # Verify employee profile was created automatically
        try:
            employee = Employee.objects.get(user=user)
            print(f"   ✓ User created successfully: {user.username}")
            print(f"   ✓ Employee profile auto-created: {employee.name}")
            print(f"   ✓ Department: {employee.department}")
            print(f"   ✓ Role: {employee.role}")
        except Employee.DoesNotExist:
            print("   ✗ FAILED: Employee profile was NOT created!")
            return False
            
    except Exception as e:
        print(f"   ✗ FAILED: Error creating employee: {e}")
        return False
    
    # Test login with credentials
    print("\n2. Testing employee login with Employee ID and Password...")
    try:
        authenticated_user = authenticate(
            username='test_new_employee_001',
            password='secure_password_123'
        )
        
        if authenticated_user:
            if not authenticated_user.is_staff:
                print("   ✓ Login SUCCESSFUL!")
                print(f"   ✓ Authenticated as: {authenticated_user.username}")
                print(f"   ✓ Is Employee (not staff): {not authenticated_user.is_staff}")
            else:
                print("   ✗ FAILED: User is marked as staff (should be employee)")
                return False
        else:
            print("   ✗ FAILED: Authentication failed - credentials not working!")
            return False
            
    except Exception as e:
        print(f"   ✗ FAILED: Error during authentication: {e}")
        return False
    
    # Test wrong password rejection
    print("\n3. Testing wrong password rejection...")
    try:
        wrong_auth = authenticate(
            username='test_new_employee_001',
            password='wrong_password'
        )
        
        if wrong_auth is None:
            print("   ✓ Wrong password correctly rejected")
        else:
            print("   ✗ FAILED: Wrong password was accepted!")
            return False
    except Exception as e:
        print(f"   ✗ FAILED: Error testing wrong password: {e}")
        return False
    
    print("\n✅ ISSUE #1 FIXED: New Employee Login is working correctly!")
    return True

def test_task_assignment():
    """Test Issue #2: Task Assignment for New Employees"""
    print("\n" + "="*60)
    print("TEST 2: Task Assignment for New Employees")
    print("="*60)
    
    # Get the test employee created in Test 1
    try:
        employee = Employee.objects.get(user__username='test_new_employee_001')
        print(f"\n1. Using employee: {employee.name} (ID: {employee.id})")
    except Employee.DoesNotExist:
        print("   ✗ FAILED: Test employee not found. Run Test 1 first!")
        return False
    
    # Create a test task
    print("\n2. Assigning task to new employee...")
    try:
        task = Task.objects.create(
            employee=employee,
            task_name='Test Task - Verify Assignment',
            description='This is a test task to verify task assignment is working for new employees.',
            completion_status='Pending',
            hours_worked=0.0
        )
        
        print(f"   ✓ Task created successfully")
        print(f"   ✓ Task ID: {task.id}")
        print(f"   ✓ Assigned to: {task.employee.name}")
        print(f"   ✓ Task Name: {task.task_name}")
        print(f"   ✓ Status: {task.completion_status}")
        
    except Exception as e:
        print(f"   ✗ FAILED: Error creating task: {e}")
        return False
    
    # Verify task is linked to employee
    print("\n3. Verifying task-employee relationship...")
    try:
        employee_tasks = Task.objects.filter(employee=employee)
        task_count = employee_tasks.count()
        
        if task_count > 0:
            print(f"   ✓ Employee has {task_count} task(s) assigned")
            
            # Check if our test task is in the list
            test_task = employee_tasks.filter(id=task.id).first()
            if test_task:
                print(f"   ✓ Test task found in employee's task list")
                print(f"   ✓ Task details accessible: {test_task.description[:50]}...")
            else:
                print("   ✗ FAILED: Test task not found in employee's tasks!")
                return False
        else:
            print("   ✗ FAILED: No tasks found for employee!")
            return False
            
    except Exception as e:
        print(f"   ✗ FAILED: Error verifying task relationship: {e}")
        return False
    
    # Test updating task progress
    print("\n4. Testing employee task progress update...")
    try:
        task.progress_description = "Working on this task. Progress is good."
        task.completion_status = 'In Progress'
        task.hours_worked = 2.5
        task.save()
        
        # Reload from database
        task.refresh_from_db()
        
        if task.progress_description and task.completion_status == 'In Progress':
            print(f"   ✓ Progress update saved successfully")
            print(f"   ✓ New status: {task.completion_status}")
            print(f"   ✓ Progress note: {task.progress_description[:40]}...")
        else:
            print("   ✗ FAILED: Progress update not saved properly!")
            return False
            
    except Exception as e:
        print(f"   ✗ FAILED: Error updating task progress: {e}")
        return False
    
    print("\n✅ ISSUE #2 FIXED: Task Assignment is working correctly!")
    return True

def test_ai_productivity_clustering():
    """Test Issue #3: AI Productivity Clustering (K-Means)"""
    print("\n" + "="*60)
    print("TEST 3: AI Productivity Clustering (K-Means)")
    print("="*60)
    
    # Ensure we have test data
    print("\n1. Preparing test data...")
    try:
        # Create attendance record for test employee
        from datetime import date
        employee = Employee.objects.get(user__username='test_new_employee_001')
        
        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=date.today(),
            defaults={
                'status': 'Present',
                'login_time': '2026-03-23 09:00:00',
                'logout_time': '2026-03-23 17:00:00',
                'total_working_hours': 8.0
            }
        )
        print(f"   ✓ Attendance record ready")
        
    except Exception as e:
        print(f"   ⚠ Warning: Could not create attendance record: {e}")
    
    # Run productivity calculation
    print("\n2. Running K-Means clustering algorithm...")
    try:
        df = calculate_productivity_scores()
        
        if df is not None:
            print(f"   ✓ K-Means clustering executed successfully")
            print(f"   ✓ Processed {len(df)} employee(s)")
            print(f"   ✓ Score range: {df['score'].min():.2f} to {df['score'].max():.2f}")
        else:
            print("   ⚠ No productivity data available (no employees)")
            
    except Exception as e:
        print(f"   ✗ FAILED: Error in K-Means clustering: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Check productivity records
    print("\n3. Verifying productivity records in database...")
    try:
        productivities = Productivity.objects.all()
        prod_count = productivities.count()
        
        if prod_count > 0:
            print(f"   ✓ Found {prod_count} productivity record(s)")
            
            # Check test employee's productivity
            try:
                emp_productivity = Productivity.objects.get(employee=employee)
                
                cluster_labels = {0: 'High Performer', 1: 'Average Performer', 2: 'Needs Improvement'}
                cluster_label = cluster_labels.get(emp_productivity.cluster_group, 'Unknown')
                
                print(f"   ✓ Test Employee Productivity:")
                print(f"      - Score: {emp_productivity.productivity_score:.2f}")
                print(f"      - Cluster: {emp_productivity.cluster_group} ({cluster_label})")
                
                # Verify cluster is valid (0, 1, or 2)
                if emp_productivity.cluster_group in [0, 1, 2]:
                    print(f"   ✓ Valid cluster assignment")
                else:
                    print(f"   ✗ Invalid cluster: {emp_productivity.cluster_group}")
                    return False
                    
            except Productivity.DoesNotExist:
                print("   ✗ FAILED: No productivity record for test employee!")
                return False
        else:
            print("   ✗ FAILED: No productivity records found!")
            return False
            
    except Exception as e:
        print(f"   ✗ FAILED: Error checking productivity records: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test with multiple employees (if available)
    print("\n4. Testing clustering with multiple employees...")
    try:
        total_employees = Employee.objects.count()
        if total_employees >= 3:
            print(f"   ✓ Have {total_employees} employees (sufficient for 3 clusters)")
            
            # Check cluster distribution
            cluster_distribution = {}
            for i in [0, 1, 2]:
                count = Productivity.objects.filter(cluster_group=i).count()
                cluster_distribution[i] = count
            
            print(f"   ✓ Cluster distribution:")
            print(f"      - High Performers (0): {cluster_distribution[0]}")
            print(f"      - Average Performers (1): {cluster_distribution[1]}")
            print(f"      - Needs Improvement (2): {cluster_distribution[2]}")
        else:
            print(f"   ℹ Only {total_employees} employee(s) - clustering will use fallback logic")
            
    except Exception as e:
        print(f"   ✗ FAILED: Error analyzing cluster distribution: {e}")
        return False
    
    print("\n✅ ISSUE #3 FIXED: AI Productivity Clustering is working correctly!")
    return True

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("COMPREHENSIVE FIX VERIFICATION TEST")
    print("ML-Powered Employee Motivation & Productivity Tracker")
    print("="*60)
    
    results = {
        'Issue #1 (Employee Login)': None,
        'Issue #2 (Task Assignment)': None,
        'Issue #3 (AI Clustering)': None
    }
    
    # Test 1: Employee Login
    results['Issue #1 (Employee Login)'] = test_employee_creation_and_login()
    
    # Test 2: Task Assignment
    results['Issue #2 (Task Assignment)'] = test_task_assignment()
    
    # Test 3: AI Clustering
    results['Issue #3 (AI Clustering)'] = test_ai_productivity_clustering()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for issue, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {issue}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL ISSUES FIXED SUCCESSFULLY!")
        print("="*60)
        print("\nSummary of Fixes:")
        print("1. ✅ New Employee Login - Working")
        print("2. ✅ Task Assignment - Working")
        print("3. ✅ AI Productivity Clustering - Working")
        print("\nThe system is now fully functional!")
    else:
        print("⚠ SOME ISSUES REMAIN")
        print("="*60)
        print("\nPlease review the failed tests above.")
    
    # Cleanup
    print("\n\nNote: Test data has been created for verification.")
    print("You can manually delete test users via Django admin if needed.")
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
