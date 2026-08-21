import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim

from accounts.models import BloodBankProfile, DonorProfile, User
from blood_requests.models import BloodRequest
from drives.models import DonationDrive
from inventory.models import BloodUnit

DEMO_PASSWORD = 'raktkosh123'
DEMO_DONOR_CITY = 'Pune, India'
DEMO_DONOR_BLOOD_GROUP = 'O+'
DEMO_BANK_NAME = 'Demo Blood Bank'
DEMO_BANK_ADDRESS = 'FC Road'
DEMO_BANK_CITY = 'Pune, India'
DEMO_BANK_PHONE = '020-1234567'

REQUEST_CITIES = [
    ('Mumbai, India', 'B+', 2),
    ('Bengaluru, India', 'O-', 1),
    ('Delhi, India', 'A+', 3),
    ('Kolkata, India', 'AB+', 1),
    ('Hyderabad, India', 'O+', 2),
]

DRIVE_TITLES = [
    ('Community Blood Donation Camp', 10),
    ('World Blood Donor Day Drive', 25),
    ('College Campus Donation Drive', 40),
]

STOCK_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'O+', 'O-']


class Command(BaseCommand):
    help = (
        "Create (or reuse) a 'Demo User' donor account and a 'Demo Blood Bank' bank "
        f"account (password '{DEMO_PASSWORD}'), then populate them with a few blood "
        "requests, drives, and blood stock so there's real-looking content to show. "
        "Fully self-contained and idempotent — safe to run on every deploy."
    )

    def handle(self, *args, **options):
        geolocator = Nominatim(user_agent='raktkosh-populate', timeout=10)
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

        with transaction.atomic():
            donor = self._get_or_create_demo_donor(geocode)
            bank = self._get_or_create_demo_bank(geocode)
            if donor is not None:
                self._create_requests(donor.get_full_name(), geocode)
            if bank is not None:
                self._create_drives(bank)
                self._create_stock(bank)

        self.stdout.write(self.style.SUCCESS('Demo content ready.'))

    def _get_or_create_demo_donor(self, geocode):
        user, created = User.objects.get_or_create(
            username='demo_donor',
            defaults={'first_name': 'Demo', 'last_name': 'User', 'role': User.Role.DONOR},
        )
        if created:
            user.set_password(DEMO_PASSWORD)
            user.save()
        if not hasattr(user, 'donor_profile'):
            result = geocode(DEMO_DONOR_CITY)
            if result is None:
                self.stdout.write(self.style.WARNING(f'Could not geocode {DEMO_DONOR_CITY} for demo donor'))
                return None
            DonorProfile.objects.create(
                user=user,
                blood_group=DEMO_DONOR_BLOOD_GROUP,
                city=DEMO_DONOR_CITY,
                latitude=result.latitude,
                longitude=result.longitude,
            )
        return user

    def _get_or_create_demo_bank(self, geocode):
        user, created = User.objects.get_or_create(
            username='demo_bank', defaults={'role': User.Role.BANK},
        )
        if created:
            user.set_password(DEMO_PASSWORD)
            user.save()
        if hasattr(user, 'bank_profile'):
            return user.bank_profile
        result = geocode(f'{DEMO_BANK_ADDRESS}, {DEMO_BANK_CITY}')
        if result is None:
            self.stdout.write(self.style.WARNING(f'Could not geocode {DEMO_BANK_ADDRESS}, {DEMO_BANK_CITY}'))
            return None
        return BloodBankProfile.objects.create(
            user=user,
            bank_name=DEMO_BANK_NAME,
            address=DEMO_BANK_ADDRESS,
            city=DEMO_BANK_CITY,
            phone=DEMO_BANK_PHONE,
            latitude=result.latitude,
            longitude=result.longitude,
        )

    def _create_requests(self, requester_name, geocode):
        for city, group, units in REQUEST_CITIES:
            if BloodRequest.objects.filter(requester_name=requester_name, city=city, blood_group=group).exists():
                continue
            result = geocode(city)
            if result is None:
                self.stdout.write(self.style.WARNING(f'Could not geocode {city}, skipping'))
                continue
            BloodRequest.objects.create(
                requester_name=requester_name,
                phone='9876543210',
                blood_group=group,
                units_needed=units,
                city=city,
                latitude=result.latitude,
                longitude=result.longitude,
            )
            self.stdout.write(f'  request: {group} in {city}')

    def _create_drives(self, bank):
        today = date.today()
        for title, days_ahead in DRIVE_TITLES:
            DonationDrive.objects.get_or_create(
                bank=bank,
                title=title,
                defaults={
                    'address': bank.address,
                    'city': bank.city,
                    'date': today + timedelta(days=days_ahead),
                    'latitude': bank.latitude,
                    'longitude': bank.longitude,
                },
            )

    def _create_stock(self, bank):
        today = date.today()
        for group in STOCK_GROUPS:
            BloodUnit.objects.get_or_create(
                bank=bank,
                blood_group=group,
                defaults={
                    'quantity': random.randint(3, 20),
                    'collected_on': today - timedelta(days=random.randint(1, 20)),
                },
            )
