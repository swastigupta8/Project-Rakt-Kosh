from django.contrib import messages
from django.shortcuts import redirect, render

from accounts.decorators import bank_required
from core.constants import BLOOD_GROUPS
from core.geo import geocode, sorted_by_distance

from .forms import BloodUnitForm
from .models import BloodUnit


def search(request):
    """Public search: which nearby blood banks have active stock of a given group?"""
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
                entry = stock_by_bank.setdefault(unit.bank_id, {'bank': unit.bank, 'groups': {}})
                entry['groups'][unit.blood_group] = entry['groups'].get(unit.blood_group, 0) + unit.quantity

            banks = [entry['bank'] for entry in stock_by_bank.values()]
            ranked_banks = sorted_by_distance(banks, lat, lng)
            results = [
                {
                    'bank': bank,
                    'distance_km': bank.distance_km,
                    'groups': stock_by_bank[bank.id]['groups'],
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
