from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .models import BloodBankProfile, DonorProfile, User

FAKE_COORDS = (18.5204, 73.8567)  # Pune


class DonorRegistrationTests(TestCase):
    @patch('accounts.forms.geocode', return_value=FAKE_COORDS)
    def test_register_donor_creates_user_and_profile(self, mock_geocode):
        response = self.client.post(reverse('accounts:register_donor'), {
            'username': 'testdonor',
            'email': 'donor@example.com',
            'first_name': 'Test',
            'last_name': 'Donor',
            'blood_group': 'O+',
            'city': 'Pune, India',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='testdonor')
        self.assertEqual(user.role, User.Role.DONOR)
        self.assertTrue(DonorProfile.objects.filter(user=user).exists())

    @patch('accounts.forms.geocode', return_value=None)
    def test_register_donor_unresolvable_city_shows_error(self, mock_geocode):
        response = self.client.post(reverse('accounts:register_donor'), {
            'username': 'testdonor2',
            'email': 'donor2@example.com',
            'blood_group': 'O+',
            'city': 'Nowhereville',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='testdonor2').exists())


class BankRegistrationTests(TestCase):
    @patch('accounts.forms.geocode', return_value=FAKE_COORDS)
    def test_register_bank_creates_user_and_profile(self, mock_geocode):
        response = self.client.post(reverse('accounts:register_bank'), {
            'username': 'testbank',
            'email': 'bank@example.com',
            'bank_name': 'Test Blood Bank',
            'address': '123 Main St',
            'city': 'Pune, India',
            'phone': '1234567890',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='testbank')
        self.assertEqual(user.role, User.Role.BANK)
        self.assertTrue(BloodBankProfile.objects.filter(user=user).exists())


class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='loginuser', password='ComplexPass123!', role=User.Role.DONOR)

    def test_login_succeeds(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'loginuser', 'password': 'ComplexPass123!',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_fails_with_wrong_password(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'loginuser', 'password': 'wrong',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class RoleAccessTests(TestCase):
    def setUp(self):
        self.donor = User.objects.create_user(username='donor1', password='pass12345', role=User.Role.DONOR)
        DonorProfile.objects.create(user=self.donor, blood_group='A+', city='Pune', latitude=18.5, longitude=73.8)
        self.client.force_login(self.donor)

    def test_donor_cannot_access_bank_only_view(self):
        response = self.client.get(reverse('inventory:add_unit'))
        self.assertEqual(response.status_code, 403)

    def test_anonymous_is_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse('inventory:my_inventory'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)
