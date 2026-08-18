from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import bank_required
from core.geo import sorted_by_distance

from .forms import BloodRequestForm
from .models import BloodRequest


def submit(request):
    """Public: no account required — a patient in an emergency may not have one."""
    if request.method == 'POST':
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Your blood request has been submitted. Nearby blood banks will be able to see it.",
            )
            return redirect('core:home')
    else:
        form = BloodRequestForm()
    return render(request, 'blood_requests/submit.html', {'form': form})


@bank_required
def pending(request):
    bank = request.user.bank_profile
    pending_requests = list(BloodRequest.objects.filter(status=BloodRequest.Status.PENDING))
    ranked = sorted_by_distance(pending_requests, bank.latitude, bank.longitude)
    return render(request, 'blood_requests/pending.html', {'results': ranked})


@bank_required
def mark_fulfilled(request, pk):
    if request.method == 'POST':
        blood_request = get_object_or_404(BloodRequest, pk=pk)
        blood_request.status = BloodRequest.Status.FULFILLED
        blood_request.save()
        messages.success(request, 'Marked as fulfilled.')
    return redirect('blood_requests:pending')
