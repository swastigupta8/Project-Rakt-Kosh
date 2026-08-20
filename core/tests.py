from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from accounts.models import BloodBankProfile, DonorProfile, User
from blood_requests.models import BloodRequest
from core.geo import distance_km, sorted_by_distance
from drives.models import DonationDrive
from inventory.models import BloodUnit


class HomeViewTests(TestCase):
    def test_home_loads_for_anonymous_visitor(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Manage your bank')

    def test_home_shows_donor_actions_for_donor(self):
        donor = User.objects.create_user(username='donor1', password='pass12345', role=User.Role.DONOR)
        DonorProfile.objects.create(user=donor, blood_group='A+', city='Pune', latitude=18.5, longitude=73.8)
        self.client.force_login(donor)

        response = self.client.get(reverse('core:home'))

        self.assertContains(response, 'Find Blood')
        self.assertContains(response, 'Request Blood')
        self.assertContains(response, 'Find Drives')
        self.assertNotContains(response, 'Manage Inventory')

    def test_home_shows_bank_dashboard_for_bank(self):
        bank_user = User.objects.create_user(username='bankuser', password='pass12345', role=User.Role.BANK)
        BloodBankProfile.objects.create(
            user=bank_user, bank_name='Test Bank', address='a', city='Pune', latitude=18.5, longitude=73.8,
        )
        self.client.force_login(bank_user)

        response = self.client.get(reverse('core:home'))

        self.assertContains(response, 'Test Bank')
        self.assertContains(response, 'Manage Inventory')
        self.assertContains(response, 'Post a Drive')
        self.assertContains(response, 'Pending Requests')


class PopulateDemoContentTests(TestCase):
    def test_missing_accounts_is_a_no_op(self):
        call_command('populate_demo_content', donor='nope', bank='nope')
        self.assertEqual(BloodRequest.objects.count(), 0)

    @patch('core.management.commands.populate_demo_content.RateLimiter', lambda func, **kwargs: func)
    @patch('core.management.commands.populate_demo_content.Nominatim')
    def test_populates_and_is_idempotent(self, mock_nominatim_cls):
        fake_result = MagicMock(latitude=18.52, longitude=73.85)
        mock_nominatim_cls.return_value.geocode.return_value = fake_result

        User.objects.create_user(
            username='swastigupta', password='x', first_name='Swasti', last_name='Gupta', role=User.Role.DONOR,
        )
        bank_user = User.objects.create_user(username='testbloodbank', password='x', role=User.Role.BANK)
        bank = BloodBankProfile.objects.create(
            user=bank_user, bank_name='Test Blood Bank', address='addr', city='Pune',
            latitude=18.5204, longitude=73.8567,
        )

        call_command('populate_demo_content')

        self.assertEqual(BloodRequest.objects.filter(requester_name='Swasti Gupta').count(), 5)
        self.assertEqual(DonationDrive.objects.filter(bank=bank).count(), 3)
        self.assertEqual(BloodUnit.objects.filter(bank=bank).count(), 7)

        call_command('populate_demo_content')

        self.assertEqual(BloodRequest.objects.filter(requester_name='Swasti Gupta').count(), 5)
        self.assertEqual(DonationDrive.objects.filter(bank=bank).count(), 3)
        self.assertEqual(BloodUnit.objects.filter(bank=bank).count(), 7)


class DistanceHelperTests(TestCase):
    def test_distance_km_same_point_is_zero(self):
        self.assertAlmostEqual(distance_km(18.52, 73.85, 18.52, 73.85), 0, places=3)

    def test_distance_km_pune_to_mumbai_is_roughly_right(self):
        d = distance_km(18.5204, 73.8567, 19.0760, 72.8777)
        self.assertTrue(100 < d < 180, f'expected ~120-150km, got {d}')

    def test_sorted_by_distance_orders_nearest_first(self):
        class Place:
            def __init__(self, lat, lon):
                self.latitude = lat
                self.longitude = lon

        near = Place(18.5204, 73.8567)  # Pune
        far = Place(28.7041, 77.1025)  # Delhi
        origin_lat, origin_lon = 18.5204, 73.8567

        result = sorted_by_distance([far, near], origin_lat, origin_lon)

        self.assertEqual(result[0], near)
        self.assertEqual(result[1], far)
        self.assertLess(near.distance_km, far.distance_km)
