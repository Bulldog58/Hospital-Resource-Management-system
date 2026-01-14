import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_settings.settings')
django.setup()

User = get_user_model()
username = os.environ.get('felloh', 'admin')
password = os.environ.get('passward', 'YourSecurePassword123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, password)
    print(f"Superuser '{username}' created successfully!")
else:
    print(f"Superuser '{username}' already exists.")