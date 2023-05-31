from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import (CreateView, DetailView, ListView, TemplateView,
                                  UpdateView, View)

from .models import Cohort
from .forms import CohortCreateForm


# Create your views here.
class CohortCreateFormView(LoginRequiredMixin,PermissionRequiredMixin, CreateView):
    form_class = CohortCreateForm
    template_name = "admin/cohort_create_form.html"


class TutorCreateView(LoginRequiredMixin,PermissionRequiredMixin,CreateView):
    form_class = TutorCreationForm
    template_name = "admin/tutor_create_form.html"


class TutorUpdateView(LoginRequiredMixin,PermissionRequiredMixin, UpdateView):
    model = Tutor
    template_name = "admin/tutor_update_form.html"
    fields = "__all__"

    def form_valid(self, form):
        return super().form_valid(form)