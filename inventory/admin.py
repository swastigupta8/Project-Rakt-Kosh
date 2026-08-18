from django.contrib import admin

from .models import BloodUnit


@admin.register(BloodUnit)
class BloodUnitAdmin(admin.ModelAdmin):
    list_display = ('bank', 'blood_group', 'quantity', 'collected_on', 'is_expired')
    list_filter = ('blood_group',)
