import re
from django import forms
from django.core.exceptions import ValidationError
from django.core.files.base import File
from django.db.models.base import Model
from django.forms import ModelForm, inlineformset_factory
from django.forms.utils import ErrorList
from .models import Course, Topic, SubTopic
from accounts.models import User, Tutor
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
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)

    class Meta:
        model = Tutor
        fields = ['first_name', 'last_name', 'picture', 'github_link', 'linkedin_link', 'twitter_link']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
           

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

