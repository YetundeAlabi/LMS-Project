from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from lms_admin.models import Cohort, Track
from .models import Tutor, Student

User = get_user_model()

class SignUpForm(UserCreationForm):
    
    first_name = forms.CharField(max_length=100, help_text='First Name')
    last_name = forms.CharField(max_length=100, help_text='Last Name')
    email = forms.EmailField(max_length=150, help_text='Email')
    
    class Meta:
        model = User
        fields = ("first_name", "last_name", 'password1', 'password2')
        

class UserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100,
                                 widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=100,
                                 widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Last Name'}))
    email = forms.EmailField(max_length=150,
                              widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Email'}))
    track = forms.ModelMultipleChoiceField(
        queryset= Track.objects.all(),
        widget = forms.SelectMultiple(attrs={"class": "form-control"})
    )
    password = forms.CharField(label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter Password'}))
    password2 = forms.CharField(label="Password confirmation",
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter Password'}))
    

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", 'password', 'password2', "track")


    def clean_password2(self):
        print(self.cleaned_data)
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password != password2:
            raise ValidationError("Passwords don't match")
        return password


    def save(self, commit=True):
        user = User.objects.create_user(
            first_name = self.cleaned_data["first_name"],
            last_name = self.cleaned_data["last_name"],
            email = self.cleaned_data["email"],
            password = self.cleaned_data["password"]
        )

        tutor = Tutor.objects.create(
            user=user,
            track=self.cleaned_data["track"])
        
        tutor.save()


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


class TutorProfileUpdateForm(forms.ModelForm):
    
    class Meta:
        model = Tutor
        exclude = ("is_verified", "is_suspended")


class StudentProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Student
        exclude = ("is_verified", "is_suspended")
