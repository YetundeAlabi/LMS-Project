from django import forms

from lms_admin.models import Track
import csv

class TrackForm(forms.ModelForm):
    
    class Meta:
        model = Track
        fields = ('name', 'slug', 'description', 'is_completed',)


class StudentImportForm(forms.Form):
    csv_file = forms.FileField(label='CSV File')
    
    def process_csv(self):
        csv_file = self.cleaned_data['csv_file']
        students = []
        reader = csv.DictReader(csv_file)
        for row in reader:
            student = {
                'username': row['Username'],
                'email': row['Email'],
                'is_verified': row['Is Verified'].lower() == 'true',
                'is_suspended': row['Is Suspended'].lower() == 'true',
                'is_deleted': row['Is Deleted'].lower() == 'true',
            }
            students.append(student)
        return students


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
    
