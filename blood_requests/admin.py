from django.contrib import admin

from .models import BloodRequest


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ('requester_name', 'blood_group', 'units_needed', 'city', 'status', 'created_at')
    list_filter = ('status', 'blood_group')
