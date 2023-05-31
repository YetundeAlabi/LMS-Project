from .models import Course, Topic, SubTopic
from django.forms import ModelForm

class CourseForm(ModelForm):

    class Meta:
        fields=("title", "description")