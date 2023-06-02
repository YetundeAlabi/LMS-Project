from django import forms

from lms_admin.models import Track

class TrackForm(forms.ModelForm):
    
    class Meta:
        model = Track
        fields = ("name, slug, description, is_completed",)

from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Cohort

def validate_current_year(value):
    current_year = timezone.now().year
    if value < current_year:
        raise ValidationError(f"Year must be {current_year} or later.")
    

class CohortCreateForm(forms.ModelForm):

    class Meta:
        model = Cohort
        fields = ('year',)

    def clean_year(self):
        year = self.cleaned_data.get('year')
        validate_current_year(year)
        return year
    
