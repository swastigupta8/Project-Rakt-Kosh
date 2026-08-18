from django.db import models

from core.constants import BLOOD_GROUPS


class BloodRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        FULFILLED = 'fulfilled', 'Fulfilled'

    requester_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    units_needed = models.PositiveIntegerField(default=1)
    city = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.blood_group} x{self.units_needed} for {self.requester_name}"
