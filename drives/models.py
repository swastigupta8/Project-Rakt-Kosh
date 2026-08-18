from django.db import models

from accounts.models import BloodBankProfile


class DonationDrive(models.Model):
    bank = models.ForeignKey(BloodBankProfile, on_delete=models.CASCADE, related_name='drives')
    title = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    date = models.DateField()
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.title} @ {self.bank.bank_name} ({self.date})"
