from django.forms.models import BaseModelForm
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Course, Topic, SubTopic
from django.contrib import messages
from .forms import CourseForm
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from accounts.models import Tutor

class OwnerMixin():
    def get_queryset(self):
        queryset= super().get_queryset()
        return queryset.filter(course_tutor=self.request.user.tutor)
       
class CourseListView(OwnerMixin, ListView):
    model = Course
    queryset = Course.active_objects.all()
    context_object_name = 'courses'

class CourseDetail(OwnerMixin, DetailView):
    model = Course
    context_object_name = 'course'
    slug_field= 'slug'
    slug_url_kwarg= 'course_slug'
    template_name = 'tutor/course_detail.html'

class CourseCreateView(OwnerMixin, CreateView):    
    model=Course
    form_class= CourseForm
    success_url = reverse_lazy('course:course_list')
    success_message= "Course Created Successfully" 
    template_name = 'tutor/course_create_update.html'

    def form_valid(self, form):
        form.instance.course_tutor=self.request.user
        return super().form_valid(form)

class CourseUpdateView(OwnerMixin, SuccessMessageMixin, UpdateView):    
    model = Course
    slug_field= 'slug'
    slug_url_kwarg= 'course_slug'
    success_url = reverse_lazy('course:course_list')
    success_message = "Course Updated Successfully"
    template_name ='tutor/course_create_update.html'
    form_class = CourseForm

class CourseDeleteView(OwnerMixin, DeleteView):
    model = Course
    slug_field= 'slug'
    slug_url_kwarg= 'course_slug'
    success_url = reverse_lazy('course:course_list')
    template_name = 'tutor/course_delete_confirm.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        messages.info(request, 'Course deleted successfully')
        return HttpResponseRedirect(self.get_success_url())