from typing import Any
from django.core.mail import send_mail
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView, DetailView, FormView, ListView, UpdateView
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from accounts.forms import StudentCreationForm, StudentImportForm
from accounts.models import Student, Tutor, User
from lms_admin.forms import TrackForm, CohortCreateForm
from lms_admin.models import Track
from .models import Cohort
# Create your views here.

class TrackCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Track
    form = TrackForm
    template_name = 'lms_admin/track_create.html'
    success_url = reverse_lazy('track_list')

    def form_valid(self, form):
        return super().form_valid(form)
    

class TrackListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Track
    template_name = 'lms_admin/track_list.html'
    context_object_name = 'tracks'

    def get_queryset(self):
            return Track.active_objects.all()
    

class TrackDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView): 
    model = Track 
    template_name = 'lms_admin/track_detail.html'
    context_object_name = 'track'


class TrackUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Track
    form = TrackForm
    template_name = 'lms_admin/track_update.html'
    slug_url_kwarg = 'slug'
    slug_field = 'slug' 

    def get_succes_url(self):
        return self.object.get_absolute_url()


class TrackDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):

    def post (self, request, slug):
        track = Track.active_objects.get(slug=slug)
        track.is_deleted = not track.is_deleted
        track.save()


class StudentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Student
    form = StudentCreationForm
    template_name = 'lms_admin/student_create.html'
    success_url = reverse_lazy('student_list')

    def form_valid(self, form):
        user = User.objects.create_user(email=form.cleaned_data['email'], 
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
        student = Student.objects.create(user=user)


class StudentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Student
    template_name = 'lms_admin/student_list.html'
    context_object_name = 'students'

    def get_queryset(self):
            return Student.objects.all()


class StudentDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView): 
    model = Student 
    template_name = 'lms_admin/student_detail.html'
    context_object_name = 'student'


class StudentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Student
    form = StudentCreationForm
    template_name = 'lms_admin/student_update.html'
    
    def get_succes_url(self):
        return self.object.get_absolute_url()


class StudentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    def post (self, request, id):
        student = Student.objects.get(id=id)
        student.is_deleted = not student.is_deleted
        student.save()


class StudentImportView(FormView):
    template_name = 'import_students.html'
    form_class = StudentImportForm
    success_url = '/import/success/'

    def form_valid(self, form):
        students = form.process_csv()
        for student in students:
            email = student['email']
            first_name = student['first_name']
            last_name = student['last_name'] 
            # is_verified = student['is_verified']
            # is_suspended = student['is_suspended']
            # is_deleted = student['is_deleted']

            student, created = Student.objects.get_or_create(
                                                            email=email,
                                                            first_name=first_name,
                                                            last_name=last_name
                                                            )

            if created:
                subject = 'Account Setup' if created else 'Login Instructions'
                context = {
                    'first_name': first_name,
                    'verification_url': self._get_verification_url(student),
                    'login_url': self._get_login_url(student),
                }
                message = render_to_string('email_template.html', context)
                send_mail(subject, message, 'adeosunfaith0101@gmail.com', ['adeosunfaith0101@gmail.com', 'otutaiwo1@gmail.com', 'momodudaniel39@gmail.com'])

        return super().form_valid(form)

    def _get_verification_url(self, student):
            return self.request.build_absolute_uri(reverse('account_setup', args=[student.id]))

    def _get_login_url(self, student):
        if student.is_verified:
            return self.request.build_absolute_uri(reverse('login'))


class CohortCreateFormView(LoginRequiredMixin,PermissionRequiredMixin, CreateView):
    form_class = CohortCreateForm
    template_name = "admin/cohort_create_form.html"


class CohortListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Cohort
    template_name = "admin/cohort_list.html"
    context_object_name = "cohort_list"

    def get_queryset(self):
        queryset = Cohort.objects.all()
        return queryset
    
    
class TutorCreateFormView(LoginRequiredMixin,PermissionRequiredMixin,CreateView):
    # form_class = TutorCreationForm
    template_name = "admin/tutor_create_form.html"


class TutorListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Tutor
    template_name = "admin/tutor_list.html"
    context_object_name = 'tutor_list'

    def get_queryset(self):
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
        tutor = get_object_or_404(Tutor, id=kwargs['pk'])
        tutor.is_deleted = True
        tutor.save() 


class ToggleTutorSuspendView(LoginRequiredMixin, PermissionRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        tutor = get_object_or_404(Tutor, id=kwargs['pk'])
        tutor.is_suspended = not tutor.is_suspended
        tutor.save()
