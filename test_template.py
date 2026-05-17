import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_project.settings')
django.setup()

from django.template.loader import get_template

try:
    template = get_template('tracker_app/admin_employee_profile.html')
    print('Template syntax is correct')
except Exception as e:
    print(f'Template error: {e}')
    import traceback
    traceback.print_exc()