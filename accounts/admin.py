from django.contrib import admin
from django.utils import timezone
from .models import FarmerDetails, BuyerDetails


def _approve_profiles(queryset):
    """Approve profiles and sync the related User.is_active flag."""
    for profile in queryset.select_related("user"):
        profile.is_active = True
        profile.deactivate_at = None
        profile.save()
        profile.user.is_active = True
        profile.user.save(update_fields=["is_active"])


@admin.register(FarmerDetails)
class FarmerDetailsAdmin(admin.ModelAdmin):
    list_display = ("user", "is_active", "deactivate_at")
    list_filter = ("is_active",)
    actions = ["approve_selected"]

    def approve_selected(self, request, queryset):
        _approve_profiles(queryset)
    approve_selected.short_description = "Approve selected farmers"


@admin.register(BuyerDetails)
class BuyerDetailsAdmin(admin.ModelAdmin):
    list_display = ("user", "is_active", "deactivate_at")
    list_filter = ("is_active",)
    actions = ["approve_selected"]

    def approve_selected(self, request, queryset):
        _approve_profiles(queryset)
    approve_selected.short_description = "Approve selected buyers"