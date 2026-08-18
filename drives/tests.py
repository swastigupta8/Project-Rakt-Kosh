from datetime import date, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from accounts.models import BloodBankProfile, User

from .models import DonationDrive

FAKE_COORDS = (18.5204, 73.8567)  # Pune


class NearbyDrivesTests(TestCase):
    def setUp(self):
        self.bank = BloodBankProfile.objects.create(
            bank_name='Drive Bank', address='addr', city='Pune', latitude=18.5204, longitude=73.8567,
        )
        DonationDrive.objects.create(
            bank=self.bank, title='Community Drive', address='addr', city='Pune',
            date=date.today() + timedelta(days=5), latitude=18.5204, longitude=73.8567,
        )
        DonationDrive.objects.create(
            bank=self.bank, title='Past Drive', address='addr', city='Pune',
            date=date.today() - timedelta(days=5), latitude=18.5204, longitude=73.8567,
        )

    @patch('drives.views.geocode', return_value=FAKE_COORDS)
    def test_nearby_returns_upcoming_drive(self, mock_geocode):
        response = self.client.get(reverse('drives:nearby'), {'city': 'Pune, India'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Community Drive')

    @patch('drives.views.geocode', return_value=FAKE_COORDS)
    def test_nearby_excludes_past_drive(self, mock_geocode):
        response = self.client.get(reverse('drives:nearby'), {'city': 'Pune, India'})
        self.assertNotContains(response, 'Past Drive')


class CreateDriveAccessTests(TestCase):
    def test_anonymous_redirected(self):
        response = self.client.get(reverse('drives:create'))
        self.assertEqual(response.status_code, 302)

    @patch('drives.forms.geocode', return_value=FAKE_COORDS)
    def test_bank_can_create_drive(self, mock_geocode):
        bank_user = User.objects.create_user(username='bankuser', password='pass12345', role=User.Role.BANK)
        BloodBankProfile.objects.create(
            user=bank_user, bank_name='B', address='a', city='Pune', latitude=18.5, longitude=73.8,
        )
        self.client.force_login(bank_user)
        response = self.client.post(reverse('drives:create'), {
            'title': 'New Drive', 'address': 'Somewhere', 'city': 'Pune, India',
            'date': (date.today() + timedelta(days=10)).isoformat(),
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(DonationDrive.objects.filter(title='New Drive').exists())
