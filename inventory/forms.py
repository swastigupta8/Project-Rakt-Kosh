from django import forms

from core.forms import BootstrapFormMixin

from .models import BloodUnit


class BloodUnitForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = BloodUnit
        fields = ['blood_group', 'quantity', 'collected_on']
        widgets = {'collected_on': forms.DateInput(attrs={'type': 'date'})}
