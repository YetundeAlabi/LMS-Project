from django import forms
from accounts.models import Student
from accounts.models import User


class ProfileUpdateForm(forms.ModelForm):
    picture = forms.ImageField(
        label='Profile Image',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control file-upload-info', 'placeholder': 'Picture' }),
    )

    github_link = forms.URLField(
        label="Github",
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
        fields = ('picture', 'github_link', 'twitter_link', 'linkedin_link',)
