from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    ordering = ('id',)
    list_display = ('email', 'full_name', 'is_staff', 'is_superuser', 'role')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name','phone','role')}),
        ('Permissions', {'fields': ('is_active','is_staff','is_superuser')}),
    )

admin.site.register(User, UserAdmin)
