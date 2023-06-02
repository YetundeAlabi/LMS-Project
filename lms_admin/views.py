from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, UpdateView, TemplateView
from lms_admin.models import Track
from lms_admin.forms import TrackForm
# Create your views here.

class TrackCreateView(CreateView, LoginRequiredMixin, PermissionRequiredMixin):
    model = Track
    form = TrackForm
    template_name = 'Lms_admin/track_create.html'
    success_url = reverse_lazy('track_list')

    def form_valid(self, form):
        return super().form_valid(form)
    

class TrackListView(ListView, LoginRequiredMixin, PermissionRequiredMixin):
    model = Track
    template_name = 'Lms_admin/track_list.html'
    context_object_name = 'tracks'
    

class TrackDetailView(DetailView, LoginRequiredMixin, PermissionRequiredMixin): 
    model = Track 
    template_name = 'Lms_admin/track_detail.html'
    context_object_name = 'track'


class TrackUpdateView(UpdateView, LoginRequiredMixin, PermissionRequiredMixin):
    model = Track
    form = TrackForm
    template_name = 'Lms_admin/track_create.html'
    slug_url_kwarg = 'slug'
    slug_field = 'slug' 

    def get_succes_url(self):
        return self.object.get_absolute_url


class TrackDelete(View, LoginRequiredMixin, PermissionRequiredMixin):
    def post (self, request, slug):
        track = Track.active_objects.get(slug=slug)
        track.is_deleted = not track.is_deleted
        track.save()