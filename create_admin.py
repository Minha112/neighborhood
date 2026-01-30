import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neighborhood_project.settings')
django.setup()

from django.contrib.auth.models import User

# Admin credentials
username = 'admin'
email = 'admin@neighbourhood.com'
password = 'admin123'

try:
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"✗ Admin user '{username}' already exists")
    else:
        # Create superuser
        User.objects.create_superuser(username=username, email=email, password=password)
        print("=" * 50)
        print("✓ Admin user created successfully!")
        print("=" * 50)
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print("=" * 50)
        print("Access admin portal at: http://127.0.0.1:8000/admin/")
        print("=" * 50)
except Exception as e:
    print(f"✗ Error creating superuser: {e}")
