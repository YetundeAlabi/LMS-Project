import re

from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import (PasswordChangeForm, SetPasswordForm,)

from .models import Student, Tutor
from lms_admin.models import Track
# from account.models import Use

User = get_user_model()


class StudentForm(forms.ModelForm):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    
    first_name = forms.CharField(
        label='First Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    
    last_name = forms.CharField(
        label='Last Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))

    gender = forms.ChoiceField(
        label='Gender',
        choices=User.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}))

    picture = forms.ImageField(
        label="Profile picture",
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control file-upload-info', 'placeholder': 'Picture' })
    )

    address = forms.CharField(
        label='Home Address',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Home Address'}))
    
    phone_number = forms.CharField(
        label='Phone Number',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))

    github_link = forms.URLField(
        label="LinkedIn",
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Github link'}),
    )

    linkedin_link = forms.URLField(
        label="LinkedIn",
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'LinkedIn link'}),
    )

    twitter_link = forms.URLField(
        label="Twitter",
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Twitter link'}),
    )
    
    
    class Meta:
        model = Student
        fields = ["email", "first_name", "last_name", "cohort", "track", "gender", "picture",
                  "address", "phone_number", "github_link", "twitter_link", "linkedin_link",]

        labels = {
            'track': 'Track',
            'cohort': 'Cohort'
        }
        widgets = {
            'track': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Track'}),
            'cohort': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Cohort'})

        }


    def clean_github_link(self):
        github_link = self.cleaned_data.get('github_link')
        if github_link:
            github_pattern = r'^https?://(www\.)?github\.com/[\w-]+/?$'
            if not re.match(github_pattern, github_link):
                raise forms.ValidationError("Invalid GitHub link format.")
        return github_link

    def clean_linkedin_link(self):
        linkedin_link = self.cleaned_data.get('linkedin_link')
        if linkedin_link:
            linkedin_pattern = r'^https?://(www\.)?linkedin\.com/in/[\w-]+/?$'
            if not re.match(linkedin_pattern, linkedin_link):
                raise forms.ValidationError("Invalid LinkedIn link format.")
        return linkedin_link

    def clean_twitter_link(self):
        twitter_link = self.cleaned_data.get('twitter_link')
        if twitter_link:
            twitter_pattern = r'^https?://(www\.)?twitter\.com/[\w-]+/?$'
            if not re.match(twitter_pattern, twitter_link):
                raise forms.ValidationError("Invalid Twitter link format.")
        return twitter_link


""" Tutor creation form """
class TutorForm(forms.ModelForm):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    first_name = forms.CharField(
        label='First Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        label='Last Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    github_link = forms.URLField(
        label="Github",
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Github link'}),
    )
    gender = forms.ChoiceField(
        label='Gender',
        choices=User.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    linkedin_link = forms.URLField(
        label="LinkedIn",
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'LinkedIn link'}),
    )

    twitter_link = forms.URLField(
        label="Twitter",
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Twitter link'}),
    )

    picture = forms.ImageField(
        label="Profile picture",
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control file-upload-info',})
    )

    
    class Meta:
        model = Tutor
        fields = ["email", "first_name", "last_name", "track", 
                  "picture", "github_link", "twitter_link", "linkedin_link", "gender"]
        labels = {
            'track': 'Track'
        }
        widgets = {
            'track': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Track'})
        }

    def clean_github_link(self):
        github_link = self.cleaned_data.get('github_link')
        if github_link:
            github_pattern = r'^https?://(www\.)?github\.com/[\w-]+/?$'
            if not re.match(github_pattern, github_link):
                raise forms.ValidationError("Invalid GitHub link format.")
        return github_link

    def clean_linkedin_link(self):
        linkedin_link = self.cleaned_data.get('linkedin_link')
        if linkedin_link:
            linkedin_pattern = r'^https?://(www\.)?linkedin\.com/in/[\w-]+/?$'
            if not re.match(linkedin_pattern, linkedin_link):
                raise forms.ValidationError("Invalid LinkedIn link format.")
        return linkedin_link

    def clean_twitter_link(self):
        twitter_link = self.cleaned_data.get('twitter_link')
        if twitter_link:
            twitter_pattern = r'^https?://(www\.)?twitter\.com/[\w-]+/?$'
            if not re.match(twitter_pattern, twitter_link):
                raise forms.ValidationError("Invalid Twitter link format.")
        return twitter_link

     
class LoginForm(forms.Form):
    email = forms.EmailField(max_length=150, 
                             widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'id': 'email', 'placeholder': 'Enter Email Address'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'id': 'password', 'placeholder': 'Enter Password'}))


class CustomSetPasswordForm(SetPasswordForm):

    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "class": "form-control"}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label="New password confirmation",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "class": "form-control"}),
    )

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if not hasattr(self.user, "tutor"):
            self.user.students.get().is_verified = True 
            if commit:
                self.user.save()
                self.user.students.get().save()
        if commit:
            self.user.save()
        return self.user


class CustomPasswordChangeForm(PasswordChangeForm):

    error_messages = {
        "password_incorrect": "Your old password was entered incorrectly. Please enter it again.",
        "password_mismatch": "The two password fields didn’t match.",
    }
    
    old_password = forms.CharField(
        label="Old password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": " form-control", "placeholder": "Enter your old password"}),
    )
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter your new password"}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label="New password confirmation",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm your new password"}),
    )

    field_order = ["old_password", "new_password1", "new_password2"]

