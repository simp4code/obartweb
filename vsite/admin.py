from django.contrib.auth.models import User

try:
    user = User.objects.get(username='adminuser')
    # User found, proceed with operations
except User.DoesNotExist:
    # Handle case when user does not exist
    print("User does not exist")
