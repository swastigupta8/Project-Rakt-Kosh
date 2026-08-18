from django.contrib import admin

from .models import DonationDrive


@admin.register(DonationDrive)
class DonationDriveAdmin(admin.ModelAdmin):
    list_display = ('title', 'bank', 'city', 'date')
    list_filter = ('city',)
