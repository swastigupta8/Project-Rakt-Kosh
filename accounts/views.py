from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from .forms import BankRegisterForm, DonorRegisterForm, RaktKoshAuthenticationForm


def register_donor(request):
    if request.method == 'POST':
        form = DonorRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('core:home')
    else:
        form = DonorRegisterForm()
    return render(request, 'accounts/register_donor.html', {'form': form})


def register_bank(request):
    if request.method == 'POST':
        form = BankRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('core:home')
    else:
        form = BankRegisterForm()
    return render(request, 'accounts/register_bank.html', {'form': form})


class RaktKoshLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = RaktKoshAuthenticationForm


class RaktKoshLogoutView(LogoutView):
    pass
