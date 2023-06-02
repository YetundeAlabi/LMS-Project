from typing import Any
from .models import Course, Topic, SubTopic
from django.forms import ModelForm
from django.forms import inlineformset_factory


class CourseForm(ModelForm):
    class Meta:
        model=Course
        fields=("title", "description")

class TopicForm(ModelForm):
    class Meta:
        model = Topic
        fields = ("title", "description")


TopicFormSet = inlineformset_factory(Course,Topic, fields=['title',
                                                            'description'],
                                                              extra=2, can_delete=True)