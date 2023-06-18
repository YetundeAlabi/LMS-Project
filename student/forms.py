from django import forms
from accounts.models import Student
from accounts.models import User


class ProfileUpdateForm(forms.ModelForm):
    picture = forms.ImageField(
        label='Profile Image',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control file-upload-info', 'placeholder': 'Picture' }))


    class Meta:
        model = Student
        fields = ('picture' ,)
