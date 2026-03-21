from django.contrib import admin
from .models import Crop  # <-- use your real model class name

@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ("crop_id","crop_name","category","description")  # add fields like ("id","name","category") if they exist
    search_fields = ("crop_id","crop_name","category","description")  # add fields like ("name","category") if they exist