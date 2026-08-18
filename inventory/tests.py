from datetime import date, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from accounts.models import BloodBankProfile, User

from .models import BloodUnit

FAKE_COORDS = (18.5204, 73.8567)  # Pune


class BloodUnitModelTests(TestCase):
    def setUp(self):
        self.bank = BloodBankProfile.objects.create(
            bank_name='Test Bank', address='addr', city='Pune', latitude=18.5, longitude=73.8,
        )

    def test_unit_is_active_within_shelf_life(self):
        unit = BloodUnit.objects.create(bank=self.bank, blood_group='O+', quantity=5, collected_on=date.today())
        self.assertFalse(unit.is_expired)
        self.assertIn(unit, BloodUnit.objects.active())

    def test_unit_is_expired_after_shelf_life(self):
        old_date = date.today() - timedelta(days=50)
        unit = BloodUnit.objects.create(bank=self.bank, blood_group='O+', quantity=5, collected_on=old_date)
        self.assertTrue(unit.is_expired)
        self.assertNotIn(unit, BloodUnit.objects.active())


class SearchViewTests(TestCase):
    def setUp(self):
        self.bank = BloodBankProfile.objects.create(
            bank_name='Test Bank', address='addr', city='Pune', latitude=18.5204, longitude=73.8567,
        )
        BloodUnit.objects.create(bank=self.bank, blood_group='O+', quantity=5, collected_on=date.today())

    @patch('inventory.views.geocode', return_value=FAKE_COORDS)
    def test_search_returns_matching_bank(self, mock_geocode):
        response = self.client.get(reverse('inventory:search'), {'city': 'Pune, India', 'blood_group': 'O+'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Bank')

    @patch('inventory.views.geocode', return_value=FAKE_COORDS)
    def test_search_filters_out_other_blood_groups(self, mock_geocode):
        response = self.client.get(reverse('inventory:search'), {'city': 'Pune, India', 'blood_group': 'AB-'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Test Bank')

    def test_search_without_city_shows_no_results(self):
        response = self.client.get(reverse('inventory:search'))
        self.assertEqual(response.status_code, 200)


class AddUnitAccessTests(TestCase):
    def test_anonymous_redirected(self):
        response = self.client.get(reverse('inventory:add_unit'))
        self.assertEqual(response.status_code, 302)

    def test_bank_can_add_unit(self):
        bank_user = User.objects.create_user(username='bankuser', password='pass12345', role=User.Role.BANK)
        BloodBankProfile.objects.create(
            user=bank_user, bank_name='B', address='a', city='Pune', latitude=18.5, longitude=73.8,
        )
        self.client.force_login(bank_user)
        response = self.client.post(reverse('inventory:add_unit'), {
            'blood_group': 'B+', 'quantity': 3, 'collected_on': date.today().isoformat(),
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(BloodUnit.objects.filter(bank__user=bank_user).exists())
