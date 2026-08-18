import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import BloodBankProfile

DEFAULT_CSV_PATH = settings.BASE_DIR / 'data' / 'blood_banks.csv'


class Command(BaseCommand):
    help = (
        "Import real blood bank directory listings from data/blood_banks.csv (sourced from India's "
        "National Health Portal Blood Bank Directory, via data.gov.in / ArcGIS Hub open data). "
        "These become BloodBankProfile rows with no linked user account (see accounts.models.BloodBankProfile) "
        "— discoverable in search, but not login-capable, since we don't have these organizations' "
        "consent to create platform accounts for them. Safe to re-run; existing rows are skipped, not duplicated."
    )

    def add_arguments(self, parser):
        parser.add_argument('--csv', default=str(DEFAULT_CSV_PATH), help='Path to the source CSV.')

    def handle(self, *args, **options):
        csv_path = options['csv']
        created = 0
        skipped_existing = 0
        skipped_bad_row = 0

        try:
            f = open(csv_path, encoding='utf-8', newline='')
        except OSError as exc:
            self.stderr.write(self.style.ERROR(f'Could not open {csv_path}: {exc}'))
            return

        with f:
            reader = csv.DictReader(f)
            rows = list(reader)

        with transaction.atomic():
            for row in rows:
                name = (row.get('bank_name') or '').strip()
                city = (row.get('city') or '').strip()
                try:
                    lat = float(row['latitude'])
                    lng = float(row['longitude'])
                except (KeyError, TypeError, ValueError):
                    skipped_bad_row += 1
                    continue

                if not name or not city:
                    skipped_bad_row += 1
                    continue

                if BloodBankProfile.objects.filter(
                    bank_name=name, city=city, is_imported=True
                ).exists():
                    skipped_existing += 1
                    continue

                BloodBankProfile.objects.create(
                    user=None,
                    bank_name=name,
                    address=(row.get('address') or '').strip(),
                    city=city,
                    phone=(row.get('phone') or '').strip(),
                    latitude=lat,
                    longitude=lng,
                    is_imported=True,
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Imported {created} real blood bank listings '
            f'(skipped {skipped_existing} already-imported, {skipped_bad_row} malformed rows).'
        ))
