import os
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aerovault.settings')
django.setup()

from accounts.models import User

try:
    user = User.objects.get(username='riddhi203')
    user.is_staff = True
    user.save()
    print(f"User {user.username} is_staff set to True successfully.")
except User.DoesNotExist:
    print("User 'riddhi203' does not exist.")
except Exception as e:
    print(f"An error occurred: {e}")