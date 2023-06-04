import csv

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Cohort
from .models import Applicant
from lms_admin.models import Track


class TrackForm(forms.ModelForm):
    
    class Meta:
        model = Track
        fields = ('name', 'slug', 'description',)


class ApplicantForm(forms.ModelForm):

    class Meta:
        model = Applicant
        exclude = ("is_approved", "cohort")


class ApplicantChecklistForm(forms.Form):
    applicants = forms.ModelMultipleChoiceField(
        queryset=Applicant.not_approved.filter(cohort__year=timezone.now().year),
        widget=forms.CheckboxSelectMultiple,
    )


class StudentImportForm(forms.Form):
    csv_file = forms.FileField(label='CSV File')
    cohort = forms.ModelChoiceField(queryset=Cohort.objects.all(), label="Cohort")
    
    def process_csv(self):
        csv_file = self.cleaned_data['csv_file']
        students = []
        reader = csv.DictReader(csv_file)

        for row in reader:
            student = {
                'email': row['Email'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'cohort': self.cleaned_data['cohort'], 
            } # Add all student user attributes to student dictionary
            students.append(student)
        return students


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
    
