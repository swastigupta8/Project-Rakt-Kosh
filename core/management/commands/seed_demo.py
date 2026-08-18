import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim

from accounts.models import BloodBankProfile, DonorProfile, User
from blood_requests.models import BloodRequest
from core.constants import BLOOD_GROUPS
from drives.models import DonationDrive
from inventory.models import BloodUnit

DEMO_DONORS = [
    ('donor_asha', 'Asha', 'Verma', 'Pune, India', 'O+'),
    ('donor_rahul', 'Rahul', 'Nair', 'Mumbai, India', 'A+'),
    ('donor_priya', 'Priya', 'Iyer', 'Bengaluru, India', 'B-'),
    ('donor_kabir', 'Kabir', 'Shah', 'Delhi, India', 'AB+'),
]

DEMO_BANKS = [
    ('bank_sunrise', 'Sunrise City Blood Bank', 'MG Road', 'Pune, India', '020-1234567'),
    ('bank_lifeline', 'Lifeline Hospital Blood Centre', 'Marine Drive', 'Mumbai, India', '022-7654321'),
    ('bank_hope', 'Hope Trust Blood Bank', 'Indiranagar', 'Bengaluru, India', '080-9988776'),
]

DEMO_REQUESTS = [
    ('Meera Joshi', '9876500001', 'O-', 2, 'Pune, India'),
    ('Sanjay Kulkarni', '9876500002', 'B+', 1, 'Mumbai, India'),
]

DEMO_PASSWORD = 'raktkosh123'


class Command(BaseCommand):
    help = (
        'Seed the database with demo (clearly-fake, login-capable) donors, banks, '
        'inventory, drives, and requests for local testing. Safe to re-run.'
    )

    def handle(self, *args, **options):
        geolocator = Nominatim(user_agent='raktkosh-seed', timeout=10)
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

        def latlng(place):
            result = geocode(place)
            if result is None:
                raise CommandError(f"Could not geocode '{place}' — check your internet connection.")
            return result.latitude, result.longitude

        with transaction.atomic():
            self._seed_donors(latlng)
            banks = self._seed_banks(latlng)
            self._seed_inventory(banks)
            self._seed_drives(banks)
            self._seed_requests(latlng)

        self.stdout.write(self.style.SUCCESS(f'Demo data ready. All demo accounts use password "{DEMO_PASSWORD}".'))

    def _seed_donors(self, latlng):
        for username, first, last, city, blood_group in DEMO_DONORS:
            if User.objects.filter(username=username).exists():
                continue
            lat, lng = latlng(city)
            user = User.objects.create_user(
                username=username, password=DEMO_PASSWORD, first_name=first, last_name=last,
                role=User.Role.DONOR,
            )
            DonorProfile.objects.create(
                user=user, blood_group=blood_group, city=city, latitude=lat, longitude=lng
            )
            self.stdout.write(f'  created donor {username}')

    def _seed_banks(self, latlng):
        banks = []
        for username, name, address, city, phone in DEMO_BANKS:
            existing = BloodBankProfile.objects.filter(user__username=username).first()
            if existing:
                banks.append(existing)
                continue
            lat, lng = latlng(f'{address}, {city}')
            user = User.objects.create_user(username=username, password=DEMO_PASSWORD, role=User.Role.BANK)
            bank = BloodBankProfile.objects.create(
                user=user, bank_name=name, address=address, city=city, phone=phone,
                latitude=lat, longitude=lng,
            )
            banks.append(bank)
            self.stdout.write(f'  created bank {name}')
        return banks

    def _seed_inventory(self, banks):
        today = date.today()
        for bank in banks:
            for group, _label in random.sample(BLOOD_GROUPS, k=4):
                BloodUnit.objects.get_or_create(
                    bank=bank,
                    blood_group=group,
                    defaults={
                        'quantity': random.randint(2, 15),
                        'collected_on': today - timedelta(days=random.randint(1, 30)),
                    },
                )

    def _seed_drives(self, banks):
        today = date.today()
        for i, bank in enumerate(banks):
            DonationDrive.objects.get_or_create(
                bank=bank,
                title=f'{bank.bank_name} Community Donation Drive',
                defaults={
                    'address': bank.address,
                    'city': bank.city,
                    'date': today + timedelta(days=7 * (i + 1)),
                    'latitude': bank.latitude,
                    'longitude': bank.longitude,
                },
            )

    def _seed_requests(self, latlng):
        for name, phone, group, units, city in DEMO_REQUESTS:
            if BloodRequest.objects.filter(requester_name=name).exists():
                continue
            lat, lng = latlng(city)
            BloodRequest.objects.create(
                requester_name=name, phone=phone, blood_group=group, units_needed=units,
                city=city, latitude=lat, longitude=lng,
            )
