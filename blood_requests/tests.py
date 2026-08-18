from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from accounts.models import BloodBankProfile, User

from .models import BloodRequest

FAKE_COORDS = (18.5204, 73.8567)  # Pune


class SubmitRequestTests(TestCase):
    @patch('blood_requests.forms.geocode', return_value=FAKE_COORDS)
    def test_submit_creates_request(self, mock_geocode):
        response = self.client.post(reverse('blood_requests:submit'), {
            'requester_name': 'Test Patient', 'phone': '1234567890', 'blood_group': 'B+',
            'units_needed': 2, 'city': 'Pune, India',
        })
        self.assertEqual(response.status_code, 302)
        req = BloodRequest.objects.get(requester_name='Test Patient')
        self.assertEqual(req.status, BloodRequest.Status.PENDING)

    @patch('blood_requests.forms.geocode', return_value=None)
    def test_submit_unresolvable_city_shows_error(self, mock_geocode):
        response = self.client.post(reverse('blood_requests:submit'), {
            'requester_name': 'Test Patient', 'phone': '1234567890', 'blood_group': 'B+',
            'units_needed': 2, 'city': 'Nowhereville',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(BloodRequest.objects.filter(requester_name='Test Patient').exists())


class PendingRequestsTests(TestCase):
    def setUp(self):
        self.bank_user = User.objects.create_user(username='bankuser', password='pass12345', role=User.Role.BANK)
        self.bank = BloodBankProfile.objects.create(
            user=self.bank_user, bank_name='B', address='a', city='Pune', latitude=18.5204, longitude=73.8567,
        )
        self.req = BloodRequest.objects.create(
            requester_name='Near Patient', phone='1', blood_group='O+', units_needed=1,
            city='Pune', latitude=18.5204, longitude=73.8567,
        )

    def test_anonymous_redirected(self):
        response = self.client.get(reverse('blood_requests:pending'))
        self.assertEqual(response.status_code, 302)

    def test_pending_lists_request(self):
        self.client.force_login(self.bank_user)
        response = self.client.get(reverse('blood_requests:pending'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Near Patient')

    def test_mark_fulfilled_updates_status(self):
        self.client.force_login(self.bank_user)
        response = self.client.post(reverse('blood_requests:mark_fulfilled', args=[self.req.pk]))
        self.assertEqual(response.status_code, 302)
        self.req.refresh_from_db()
        self.assertEqual(self.req.status, BloodRequest.Status.FULFILLED)
