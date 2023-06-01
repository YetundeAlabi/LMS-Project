from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm
from django.core.exceptions import ValidationError
from accounts.models import User

class AdminCreateForm(UserCreationForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email",)