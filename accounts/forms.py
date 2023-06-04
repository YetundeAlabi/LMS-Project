from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from lms_admin.models import Cohort, Track

User = get_user_model()

class SignUpForm(UserCreationForm):
    
    first_name = forms.CharField(max_length=100, help_text='First Name')
    last_name = forms.CharField(max_length=100, help_text='Last Name')
    email = forms.EmailField(max_length=150, help_text='Email')
    
    class Meta:
        model = User
        fields = ("first_name", "last_name", 'password1', 'password2')


class StudentCreationForm(forms.Form):
    cohort = forms.ModelChoiceField(
        label="Cohort",
        queryset=Cohort.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Cohort'}))
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    first_name = forms.CharField(
        label='First Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(
        label='Last Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    
class TutorCreationForm(forms.Form):
    track = forms.ModelChoiceField(
        label="Track",
        queryset=Track.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Track'}))
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    first_name = forms.CharField(
        label='First Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(
        label='Last Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    
    

class LoginForm(AuthenticationForm):
    email = forms.EmailField(max_length=150, 
                             widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'id': 'email', 'placeholder': 'Enter Email Address'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'id': 'password', 'placeholder': 'Enter Password'}))


