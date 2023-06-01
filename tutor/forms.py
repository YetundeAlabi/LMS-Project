from typing import Any
from .models import Course, Topic, SubTopic
from django.forms import ModelForm

class CourseForm(ModelForm):
    class Meta:
        model=Course
        fields=("title", "description")
