import csv
from io import TextIOWrapper
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from lms_admin.models import Track
from phonenumber_field.formfields import PhoneNumberField

from .models import Applicant, Cohort


class TrackForm(forms.ModelForm):
    """Form to create Track"""
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Track Name'}),
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Track Description'}),
    )
    class Meta:
        model = Track
        fields = ('name', 'description',)

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if self.instance is not None: 
            if Track.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
                raise ValidationError('A track with the same name already exists.')
        return name


class ApplicantForm(forms.ModelForm):

    class Meta:
        model = Applicant
        exclude = ("is_approved", "cohort")

    first_name = forms.CharField(
        label='First Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        label='Last Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    gender = forms.ChoiceField(
        label='Gender',
        choices=Applicant.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    track = forms.ModelChoiceField(
        label='Track',
        queryset=Track.active_objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    address = forms.CharField(
        label='Home Address',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Home Address'})
    )
    phone_number = forms.CharField(
        label='Phone Number',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
    )


class ApplicantChecklistForm(forms.Form):
    applicants = forms.ModelMultipleChoiceField(
        queryset=Applicant.not_approved.filter(cohort__year=timezone.now().year),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-control form-control-lg'}),
    )


class StudentImportForm(forms.Form):
    csv_file = forms.FileField(label='csv_file')
    cohort = forms.ModelChoiceField(queryset=Cohort.objects.all(), label="cohort")
    
    def process_csv(self):
        csv_file = self.cleaned_data['csv_file']
        students = []

        file_wrapper = TextIOWrapper(csv_file, encoding='utf-8')
        reader = csv.DictReader(file_wrapper)

        for row in reader:
            student = {
                'email': row['email'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'gender': row['gender'],
                'track': row['track'],
                'cohort': self.cleaned_data['cohort'], 
                  
                
            } # Add all student user attributes to student dictionary
            students.append(student)
        return students


def validate_current_year(value):
    current_year = timezone.now().year
    if value < current_year:
        raise ValidationError(f"Year must be {current_year} or later.")
    

class CohortCreateForm(forms.ModelForm):

    year = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Input Cohort Year'})
    )
    
    class Meta:
        model = Cohort
        fields = ('year',)

    def clean_year(self):
        year = self.cleaned_data.get('year')
        validate_current_year(year)
        return year
    
