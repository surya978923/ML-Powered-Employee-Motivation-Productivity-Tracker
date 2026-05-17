import os
import django
import sys

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_project.settings')
django.setup()

from django.contrib.auth.models import User

def create_superuser():
    """Create a default superuser if one doesn't exist"""
    username = 'admin'
    email = 'admin@company.com'
    password = 'admin123'
    
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print(f"✓ Superuser created:")
        print(f"  Username: {username}")
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        print(f"  Login at: http://127.0.0.1:8000/admin/")
    else:
        print("✓ Superuser already exists")
        user = User.objects.get(username=username)
        print(f"  Username: {user.username}")
        print(f"  Login at: http://127.0.0.1:8000/admin/")

if __name__ == '__main__':
    create_superuser()