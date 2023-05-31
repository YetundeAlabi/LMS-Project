from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Course, Topic, SubTopic

# Create your views here.

class OwnerMixin():
    def get_queryset(self):
        queryset= super().get_queryset()
        return queryset.filter(tutor=self.request.user)

 
class CourseListView(OwnerMixin, ListView):
    model = Course
    queryset = Course.active_objects.all()
    context_object_name = 'Courses'
