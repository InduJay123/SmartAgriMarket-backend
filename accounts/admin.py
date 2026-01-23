from django.contrib import admin
from django.utils import timezone
from .models import FarmerDetails, BuyerDetails

@admin.register(FarmerDetails)
class FarmerDetailsAdmin(admin.ModelAdmin):
    list_display = ("user", "is_active", "deactivate_at")
    list_filter = ("is_active",)
    actions = ["verify_selected"]

    def verify_selected(self, request, queryset):
        queryset.update(is_active=True, deactivate_at=timezone.now())

@admin.register(BuyerDetails)
class BuyerDetailsAdmin(admin.ModelAdmin):
    list_display = ("user", "is_active", "deactivate_at")
    list_filter = ("is_active",)
    actions = ["verify_selected"]

    def verify_selected(self, request, queryset):
        queryset.update(is_active=True, deactivate_at=timezone.now())