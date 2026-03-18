from django.core.management import setup_environ;
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartagri_backend.settings')
import django
django.setup()
from django.test import RequestFactory
from accounts.admin_views import AdminUserDetailAPI
from accounts.models import User, BuyerDetails

user = User.objects.filter(role='BUYER').first()
buyer = BuyerDetails.objects.filter(user=user).first()
print(f'Before: User is_active: {user.is_active}, Buyer is_active: {buyer.is_active}')

rf = RequestFactory()
request = rf.put('/api/auth/admin/user/1/', {'is_active': False, 'is_verified': False}, content_type='application/json')
# We need to simulate the view
view = AdminUserDetailAPI.as_view()
response = view(request, user_id=user.id)
print(response.status_code)
print(response.data)

user.refresh_from_db()
buyer.refresh_from_db()
print(f'After: User is_active: {user.is_active}, Buyer is_active: {buyer.is_active}')
