from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, UpdateView, TemplateView
from lms_admin.models import Track
from lms_admin.forms import TrackForm
from accounts.models import Student
from accounts.forms import StudentCreationForm
# Create your views here.

class TrackCreateView(CreateView, LoginRequiredMixin, PermissionRequiredMixin):
    model = Track
    form = TrackForm
    template_name = 'lms_admin/track_create.html'
    success_url = reverse_lazy('track_list')

    def form_valid(self, form):
        return super().form_valid(form)
    

class TrackListView(ListView, LoginRequiredMixin, PermissionRequiredMixin):
    model = Track
    template_name = 'lms_admin/track_list.html'
    context_object_name = 'tracks'
    

class TrackDetailView(DetailView, LoginRequiredMixin, PermissionRequiredMixin): 
    model = Track 
    template_name = 'lms_admin/track_detail.html'
    context_object_name = 'track'


class TrackUpdateView(UpdateView, LoginRequiredMixin, PermissionRequiredMixin):
    model = Track
    form = TrackForm
    template_name = 'lms_admin/track_update.html'
    slug_url_kwarg = 'slug'
    slug_field = 'slug' 

    def get_succes_url(self):
        return self.object.get_absolute_url()


class TrackDeleteView(View, LoginRequiredMixin, PermissionRequiredMixin):
    def post (self, request, slug):
        track = Track.active_objects.get(slug=slug)
        track.is_deleted = not track.is_deleted
        track.save()


class StudentCreateView(CreateView, LoginRequiredMixin, PermissionRequiredMixin):
    model = Student
    form = StudentCreationForm
    template_name = 'lms_admin/student_create.html'
    success_url = reverse_lazy('student_list')

    def form_valid(self, form):
        return super().form_valid(form)


class StudentListView(ListView, LoginRequiredMixin, PermissionRequiredMixin):
    model = Student
    template_name = 'lms_admin/student_list.html'
    context_object_name = 'students'


class SudentDetailView(DetailView, LoginRequiredMixin, PermissionRequiredMixin): 
    model = Student 
    template_name = 'lms_admin/student_detail.html'
    context_object_name = 'student'


class StudentUpdateView(UpdateView, LoginRequiredMixin, PermissionRequiredMixin):
    model = Student
    form = StudentCreationForm
    template_name = 'lms_admin/student_update.html'
    
    def get_succes_url(self):
        return self.object.get_absolute_url()


class StudentDeleteView(View, LoginRequiredMixin, PermissionRequiredMixin):
    def post (self, request, id):
        student = Student.objects.get(id=id)
        student.is_deleted = not student.is_deleted
        student.save()