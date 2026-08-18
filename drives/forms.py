from django import forms

from core.forms import BootstrapFormMixin
from core.geo import geocode

from .models import DonationDrive


class DonationDriveForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = DonationDrive
        fields = ['title', 'address', 'city', 'date']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

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
        drive = super().save(commit=False)
        lat, lng = self.cleaned_coords
        drive.latitude = lat
        drive.longitude = lng
        if commit:
            drive.save()
        return drive
