from django import forms

from lms_admin.models import Track

class TrackForm(forms.ModelForm):
    
    class Meta:
        model = Track
        fields = ("name, slug, description, is_completed",)
