import re
from django import forms
from django.core.exceptions import ValidationError
from django.core.files.base import File
from django.db.models.base import Model
from django.forms import ModelForm, inlineformset_factory
from django.forms.utils import ErrorList
from .models import Course, Topic, SubTopic
from accounts.models import User, Tutor



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
        label='Profile Image',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control file-upload-info', 'placeholder': 'Picture' })
    )
    github_link = forms.URLField(
        label="LinkedIn",
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'LinkedIn link'}),
    )
    
    class Meta:
        model = Tutor
        fields = ['picture', 'github_link', 'linkedin_link', 'twitter_link']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user:
            self.fields['github_link'].initial = self.instance.user.github_link
            self.fields['linkedin_link'].initial = self.instance.user.linkedin_link
            self.fields['twitter_link'].initial = self.instance.user.twitter_link

           

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

