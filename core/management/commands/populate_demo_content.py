import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim

from accounts.models import BloodBankProfile, User
from blood_requests.models import BloodRequest
from drives.models import DonationDrive
from inventory.models import BloodUnit

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
        'Populate demo blood requests (attributed to --donor) and drives/stock '
        '(for --bank) so there is real-looking content to show. Both accounts must '
        'already exist (registered through the site) — if either is missing, this '
        'logs a warning and does nothing rather than failing, so it is safe to run '
        'unconditionally on every deploy. Safe to re-run: skips rows already created.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--donor', default='swastigupta')
        parser.add_argument('--bank', default='testbloodbank')

    def handle(self, *args, **options):
        donor = User.objects.filter(username=options['donor']).first()
        if donor is None:
            self.stdout.write(self.style.WARNING(
                f"No user '{options['donor']}' yet — skipping demo request population."
            ))
            donor = None

        bank = BloodBankProfile.objects.filter(user__username=options['bank']).first()
        if bank is None:
            self.stdout.write(self.style.WARNING(
                f"No blood bank account '{options['bank']}' yet — skipping demo drive/stock population."
            ))

        if donor is None and bank is None:
            return

        geolocator = Nominatim(user_agent='raktkosh-populate', timeout=10)
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

        with transaction.atomic():
            if donor is not None:
                self._create_requests(donor.get_full_name() or donor.username, geocode)
            if bank is not None:
                self._create_drives(bank)
                self._create_stock(bank)

        self.stdout.write(self.style.SUCCESS('Demo content populated.'))

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
