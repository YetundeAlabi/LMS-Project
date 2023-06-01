import csv

from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import (CreateView, DetailView, ListView, TemplateView,
                                  UpdateView, View)

from accounts.models import Tutor

from .models import Cohort
from .forms import CohortCreateForm


# Create your views here.
class CohortCreateFormView(LoginRequiredMixin,PermissionRequiredMixin, CreateView):
    form_class = CohortCreateForm
    template_name = "admin/cohort_create_form.html"


class CohortListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Cohort
    template_name = "admin/cohort_list.html"
    context_object_name = "cohort_list"

    def get_queryset(self) -> QuerySet[Any]:
        queryset = Cohort.objects.all()
        return queryset
    
    
class TutorCreateFormView(LoginRequiredMixin,PermissionRequiredMixin,CreateView):
    # form_class = TutorCreationForm
    template_name = "admin/tutor_create_form.html"


class TutorListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Tutor
    template_name = "admin/tutor_list.html"
    context_object_name = 'tutor_list'

    def get_queryset(self) -> QuerySet[Any]:
        return Tutor.objects.all()


class TutorUpdateView(LoginRequiredMixin,PermissionRequiredMixin, UpdateView):
    model = Tutor
    template_name = "admin/tutor_update_form.html"
    fields = "__all__"

    def form_valid(self, form):
        return super().form_valid(form)
    

class TutorDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Tutor
    template_name = "admin/tutor_detail.html"


class TutorDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    
    def post(self, request, *args, **kwargs):
        tutor = get_object_or_404(id=kwargs['pk'])
        tutor.is_deleted = True
        tutor.save() 


class ToggleTutorSuspendView(LoginRequiredMixin, PermissionRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        tutor = get_object_or_404(id=kwargs['pk'])
        suspension_status = tutor.is_suspended
        tutor.is_suspended = not suspension_status
        tutor.save()
