from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.accounts.urls')),
    path('api/v1/', include('apps.products.urls')),
    path('api/v1/', include('apps.orders.urls')),
    path('api/v1/dashboard/', include('apps.dashboard.urls')),
    path('api/v1/adminpanel/', include('apps.adminpanel.urls')),
    # path('api/v1/products/', include('apps.products.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
]
