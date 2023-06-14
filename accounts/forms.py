from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm, SetPasswordForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, password_validation

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


""" Tutor sign uo form"""
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
        
        return tutor


class StudentCreationForm(forms.Form):
    cohort = forms.ModelChoiceField(
        label="Cohort",
        queryset=Cohort.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Cohort'}))
    track = forms.ModelChoiceField(
        label="Track",
        queryset=Track.active_objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Track'}))
    gender = forms.ChoiceField(
        label='Gender',
        choices=Student.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Gender'}))
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    first_name = forms.CharField(
        label='First Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(
        label='Last Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    picture = forms.ImageField(
        label='Profile Image',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control file-upload-info', 'placeholder': 'Picture' }))

    def __init__(self, *args, **kwargs):
        kwargs.pop("instance")
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        user = User.objects.create_user(
            email=self.cleaned_data['email'], 
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'])
        
        student = Student.objects.create(user=user, 
                                        cohort=self.cleaned_data['cohort'],
                                        track=self.cleaned_data['track'],
                                        gender=self.cleaned_data['gender'],
                                        picture=self.cleaned_data['picture'])
        #student.save()
        return student


""" Tutor creation form """
class TutorCreationForm(forms.Form):

    track = forms.ModelChoiceField(
        label="Track",
        queryset=Track.active_objects.all(),
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
    
    def __init__(self, *args, **kwargs):
        kwargs.pop("instance")
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        user = User.objects.create_user(
            email=self.cleaned_data['email'], 
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'])
        
        tutor = Tutor.objects.create(user=user, 
                                        track=self.cleaned_data['track'])
        #tutor.save()
        return tutor

     
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


class CustomPasswordChangeForm(PasswordChangeForm):

    error_messages = {
        "password_incorrect": "Your old password was entered incorrectly. Please enter it again.",
        "password_mismatch": "The two password fields didn’t match.",
    }
    
    old_password = forms.CharField(
        label="Old password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": " form-control", "placeholder": "Enter your old password"}
        ),
    )
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(
            attrs={"class": " form-control", "placeholder": "Enter your new password"}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label="New password confirmation",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": " form-control", "placeholder": "Confirm your new password"}),
    )

    field_order = ["old_password", "new_password1", "new_password2"]


class TutorUpdateForm(forms.ModelForm):
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
    
    # def __init__(self, *args, **kwargs):
    #     kwargs.pop("instance")
    #     super().__init__(*args, **kwargs)

    model = User
    fields = ["email", "first_name", "last_name", "track"]

class StudentUpdateForm(forms.ModelForm):

    class Meta:
        model = Student
        exclude = ("is_verified", "is_suspended")


class ProfilePictureForm(forms.ModelForm):
    picture = forms.CharField(
        label="Profile picture",
        widget=forms.ClearableFileInput(attrs={'class': 'form_control'})
    )
