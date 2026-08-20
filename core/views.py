from django.shortcuts import render
from django.utils import timezone

from blood_requests.models import BloodRequest
from drives.models import DonationDrive
from inventory.models import BloodUnit


def home(request):
    context = {}
    user = request.user

    if user.is_authenticated and user.role == 'bank':
        bank = getattr(user, 'bank_profile', None)
        if bank:
            context['bank'] = bank
            context['active_unit_count'] = BloodUnit.objects.active().filter(bank=bank).count()
            context['upcoming_drive_count'] = DonationDrive.objects.filter(
                bank=bank, date__gte=timezone.now().date()
            ).count()
            context['pending_request_count'] = BloodRequest.objects.filter(
                status=BloodRequest.Status.PENDING
            ).count()

    return render(request, 'core/home.html', context)
