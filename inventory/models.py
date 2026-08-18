from django.db import models
from django.utils import timezone

from accounts.models import BloodBankProfile
from core.constants import BLOOD_GROUPS, BLOOD_UNIT_SHELF_LIFE_DAYS


class BloodUnitManager(models.Manager):
    def active(self):
        """Units still within their shelf life (collected within the last 42 days)."""
        cutoff = timezone.now().date() - timezone.timedelta(days=BLOOD_UNIT_SHELF_LIFE_DAYS)
        return self.get_queryset().filter(collected_on__gte=cutoff)


class BloodUnit(models.Model):
    bank = models.ForeignKey(BloodBankProfile, on_delete=models.CASCADE, related_name='blood_units')
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    quantity = models.PositiveIntegerField(help_text='Number of units/bags')
    collected_on = models.DateField()

    objects = BloodUnitManager()

    class Meta:
        ordering = ['-collected_on']

    @property
    def expires_on(self):
        return self.collected_on + timezone.timedelta(days=BLOOD_UNIT_SHELF_LIFE_DAYS)

    @property
    def is_expired(self):
        return timezone.now().date() > self.expires_on

    def __str__(self):
        return f"{self.blood_group} x{self.quantity} @ {self.bank.bank_name}"
