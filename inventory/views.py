from django.contrib import messages
from django.shortcuts import redirect, render

from accounts.decorators import bank_required
from accounts.models import BloodBankProfile
from core.constants import BLOOD_GROUPS
from core.geo import geocode, sorted_by_distance

from .forms import BloodUnitForm
from .models import BloodUnit

NEARBY_BANKS_LIMIT = 25


def search(request):
    """Public search.

    With a blood group selected: only banks that actually have that group in
    active stock (there's no point listing a bank that doesn't have it).

    With no blood group selected: the nearest banks generally, whether or not
    they currently have stock listed — most of our directory (real, imported
    facilities) doesn't have live stock until that bank registers and starts
    updating it, and hiding them entirely would make the directory data
    invisible. Each result makes clear whether its stock is live.
    """
    query_city = request.GET.get('city', '').strip()
    blood_group = request.GET.get('blood_group', '').strip()
    results = None
    error = None

    if query_city:
        coords = geocode(query_city)
        if coords is None:
            error = "We couldn't locate that city. Try being more specific, e.g. 'Pune, India'."
        else:
            lat, lng = coords
            units = BloodUnit.objects.active().select_related('bank')
            if blood_group:
                units = units.filter(blood_group=blood_group)

            stock_by_bank = {}
            for unit in units:
                entry = stock_by_bank.setdefault(unit.bank_id, {})
                entry[unit.blood_group] = entry.get(unit.blood_group, 0) + unit.quantity

            if blood_group:
                banks = [unit.bank for unit in units]
                # de-dupe while preserving one entry per bank
                banks = list({bank.id: bank for bank in banks}.values())
            else:
                banks = list(BloodBankProfile.objects.all())

            ranked_banks = sorted_by_distance(banks, lat, lng)
            if not blood_group:
                ranked_banks = ranked_banks[:NEARBY_BANKS_LIMIT]

            results = [
                {
                    'bank': bank,
                    'distance_km': bank.distance_km,
                    'groups': stock_by_bank.get(bank.id),
                }
                for bank in ranked_banks
            ]

    return render(request, 'inventory/search.html', {
        'results': results,
        'query_city': query_city,
        'blood_group': blood_group,
        'blood_groups': BLOOD_GROUPS,
        'error': error,
    })


@bank_required
def add_unit(request):
    bank = request.user.bank_profile
    if request.method == 'POST':
        form = BloodUnitForm(request.POST)
        if form.is_valid():
            unit = form.save(commit=False)
            unit.bank = bank
            unit.save()
            messages.success(request, 'Blood unit added to your inventory.')
            return redirect('inventory:my_inventory')
    else:
        form = BloodUnitForm()
    return render(request, 'inventory/add_unit.html', {'form': form})


@bank_required
def my_inventory(request):
    bank = request.user.bank_profile
    units = bank.blood_units.all()
    return render(request, 'inventory/my_inventory.html', {'units': units})
