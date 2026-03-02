"""
URL configuration for smartagri_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

# Try to import swagger/OpenAPI documentation
try:
    from rest_framework import permissions
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi
    
    # Swagger/OpenAPI schema configuration
    schema_view = get_schema_view(
        openapi.Info(
            title="SmartAgriMarket ML API",
            default_version='v1',
            description="Machine Learning API for flood prediction and agricultural insights",
            terms_of_service="https://www.smartagrimarket.com/terms/",
            contact=openapi.Contact(email="support@smartagrimarket.com"),
            license=openapi.License(name="MIT License"),
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
    )
    HAS_SWAGGER = True
except ImportError:
    HAS_SWAGGER = False
    schema_view = None

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ML API endpoints
    path('api/ml/', include('ml_api.urls')),
    
    #path('api/', include('crops.urls')),
]

# Add swagger documentation URLs if drf_yasg is installed
if HAS_SWAGGER and schema_view:
    urlpatterns += [
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    ]
