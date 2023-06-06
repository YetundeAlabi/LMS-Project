from typing import Any
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm, inlineformset_factory
from .models import Course, Topic, SubTopic


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


TopicFormSet = inlineformset_factory(Course, Topic, fields=['title', 'description'], extra=2, widgets={
    'title': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Topic Title'}),
    'description': forms.Textarea(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Topic Description'})
})
