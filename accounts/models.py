from django.contrib.auth.models import AbstractUser
from django.db import models

from core.constants import BLOOD_GROUPS


class User(AbstractUser):
    class Role(models.TextChoices):
        DONOR = 'donor', 'Donor / Patient'
        BANK = 'bank', 'Blood Bank / Hospital'

    role = models.CharField(max_length=10, choices=Role.choices)


class DonorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='donor_profile')
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    city = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    last_donation_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.blood_group})"


class BloodBankProfile(models.Model):
    """A blood bank / hospital facility.

    `user` is nullable: profiles imported from a public directory (see
    accounts/management/commands/import_real_banks.py) describe a real facility's
    location for search purposes but aren't login-capable accounts, since we don't
    have that organization's consent to create one. `user` is only set for banks
    that actually registered on the platform themselves.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='bank_profile', null=True, blank=True
    )
    bank_name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    # Real directory listings often carry several numbers in one field
    # (e.g. "011 42251800, 011 42251868, ..."), so this is deliberately
    # generous rather than a single-number width.
    phone = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_imported = models.BooleanField(default=False)

    @property
    def is_claimed(self):
        return self.user_id is not None

    def __str__(self):
        return self.bank_name
