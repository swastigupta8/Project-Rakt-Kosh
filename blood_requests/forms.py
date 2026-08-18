from django import forms

from core.forms import BootstrapFormMixin
from core.geo import geocode

from .models import BloodRequest


class BloodRequestForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = ['requester_name', 'phone', 'blood_group', 'units_needed', 'city']

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
        request_obj = super().save(commit=False)
        lat, lng = self.cleaned_coords
        request_obj.latitude = lat
        request_obj.longitude = lng
        if commit:
            request_obj.save()
        return request_obj
