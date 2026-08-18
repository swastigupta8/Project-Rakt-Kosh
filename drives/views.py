from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone

from accounts.decorators import bank_required
from core.geo import geocode, sorted_by_distance

from .forms import DonationDriveForm
from .models import DonationDrive


@bank_required
def create_drive(request):
    if request.method == 'POST':
        form = DonationDriveForm(request.POST)
        if form.is_valid():
            drive = form.save(commit=False)
            drive.bank = request.user.bank_profile
            drive.save()
            messages.success(request, 'Donation drive posted.')
            return redirect('drives:nearby')
    else:
        form = DonationDriveForm()
    return render(request, 'drives/create_drive.html', {'form': form})


def nearby(request):
    query_city = request.GET.get('city', '').strip()
    results = None
    error = None

    if query_city:
        coords = geocode(query_city)
        if coords is None:
            error = "We couldn't locate that city. Try being more specific, e.g. 'Pune, India'."
        else:
            lat, lng = coords
            upcoming = list(
                DonationDrive.objects.filter(date__gte=timezone.now().date()).select_related('bank')
            )
            results = sorted_by_distance(upcoming, lat, lng)

    return render(request, 'drives/nearby.html', {
        'results': results,
        'query_city': query_city,
        'error': error,
    })
