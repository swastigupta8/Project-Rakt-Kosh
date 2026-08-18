from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from core.constants import BLOOD_GROUPS
from core.forms import BootstrapFormMixin
from core.geo import geocode

from .models import BloodBankProfile, DonorProfile, User


class RaktKoshAuthenticationForm(BootstrapFormMixin, AuthenticationForm):
    pass


class DonorRegisterForm(BootstrapFormMixin, UserCreationForm):
    blood_group = forms.ChoiceField(choices=BLOOD_GROUPS)
    city = forms.CharField(max_length=100, help_text="e.g. 'Pune, India' — be specific so we can locate you.")

    field_order = ['username', 'email', 'first_name', 'last_name', 'blood_group', 'city', 'password1', 'password2']

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_city(self):
        city = self.cleaned_data['city']
        coords = geocode(city)
        if coords is None:
            raise forms.ValidationError(
                "We couldn't locate that city. Try a more specific name, e.g. 'Pune, India'."
            )
        self.cleaned_coords = coords
        return city

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.DONOR
        if commit:
            user.save()
            lat, lng = self.cleaned_coords
            DonorProfile.objects.create(
                user=user,
                blood_group=self.cleaned_data['blood_group'],
                city=self.cleaned_data['city'],
                latitude=lat,
                longitude=lng,
            )
        return user


class BankRegisterForm(BootstrapFormMixin, UserCreationForm):
    bank_name = forms.CharField(max_length=200)
    address = forms.CharField(max_length=300)
    city = forms.CharField(max_length=100, help_text="e.g. 'Pune, India' — be specific so we can locate you.")
    phone = forms.CharField(max_length=20, required=False)

    field_order = ['username', 'email', 'bank_name', 'address', 'city', 'phone', 'password1', 'password2']

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned = super().clean()
        city = cleaned.get('city')
        address = cleaned.get('address')
        if city:
            query = f"{address}, {city}" if address else city
            coords = geocode(query)
            if coords is None:
                self.add_error('city', "We couldn't locate that address/city. Try being more specific.")
            else:
                self.cleaned_coords = coords
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.BANK
        if commit:
            user.save()
            lat, lng = self.cleaned_coords
            BloodBankProfile.objects.create(
                user=user,
                bank_name=self.cleaned_data['bank_name'],
                address=self.cleaned_data['address'],
                city=self.cleaned_data['city'],
                phone=self.cleaned_data.get('phone', ''),
                latitude=lat,
                longitude=lng,
            )
        return user
