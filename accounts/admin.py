from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import BloodBankProfile, DonorProfile, User


class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (('Role', {'fields': ('role',)}),)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (('Role', {'fields': ('role',)}),)
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = BaseUserAdmin.list_filter + ('role',)


@admin.register(DonorProfile)
class DonorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'blood_group', 'city', 'last_donation_date')
    list_filter = ('blood_group', 'city')


@admin.register(BloodBankProfile)
class BloodBankProfileAdmin(admin.ModelAdmin):
    list_display = ('bank_name', 'city', 'is_claimed', 'is_imported')
    list_filter = ('city', 'is_imported')


admin.site.register(User, UserAdmin)
