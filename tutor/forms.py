from typing import Any
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm, inlineformset_factory
from .models import Course, Topic, SubTopic
from accounts.models import User
from django.contrib.auth.forms import UserChangeForm


class CourseForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Course title'}),
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Course Description'}),
    )

    class Meta:
        model = Course
        fields = ("title", "description")

    def clean_title(self):
        title = self.cleaned_data['title']
        instance=getattr(self, 'instance', None)
        if instance is None or instance.pk is None:
            if Course.objects.filter(title=title).exists():
                raise ValidationError("A course with this title already exists.")
        return title

class TopicForm(ModelForm):
    
    class Meta:
        model = Topic
        fields = ("title", "description")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter the title"}),
            "description": forms.Textarea(attrs={"class": "form-control", "placeholder": "Enter the description"}),
        }


TopicFormSet = inlineformset_factory(Course, Topic, fields=['title', 'description'], extra=5, widgets={
    'title': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Topic Title'}),
    'description': forms.Textarea(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Topic Description'})
})


class TutorUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

   