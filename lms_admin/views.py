import csv

from typing import Any, Dict
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView
from django.core.mail import send_mail
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View
from django.views.generic import (
    CreateView, DetailView, FormView, ListView, UpdateView, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from accounts.forms import StudentCreationForm, TutorCreationForm
from accounts.models import Student, Tutor, User
from lms_admin.forms import TrackForm, CohortCreateForm, StudentImportForm,ApplicantChecklistForm, ApplicantForm
from lms_admin.models import Track
from .models import Cohort, Applicant

# Create your views here

class DashboardView(TemplateView):
    template_name = "lms_admin/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['students'] = Student.objects.all()
        return context

# Track Views
class TrackCreateView(CreateView):
    """Track Create View"""
    model = Track
    form_class = TrackForm
    template_name = 'lms_admin/track_create.html'
    success_url = reverse_lazy('track_list')

    def form_valid(self, form):
        return super().form_valid(form)
    

class TrackListView(ListView):
    """Track List View to list all active Tracks"""
    model = Track
    template_name = 'lms_admin/track_list.html'
    context_object_name = 'tracks'

    def get_queryset(self):
            return Track.active_objects.all()
    

class TrackDetailView(DetailView): 
    """Generic Track Detail View"""
    model = Track 
    template_name = 'lms_admin/track_detail.html'
    context_object_name = 'track'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context['track_students'] = Student.objects.filter(track=obj)
        print(context['track_students'])
        print(obj)
        return context


class TrackUpdateView(UpdateView):
    """Generic Track Update View"""
    model = Track
    form_class = TrackForm
    template_name = 'lms_admin/track_update.html'
    slug_url_kwarg = 'slug'
    slug_field = 'slug' 

    def get_success_url(self):
        return self.object.get_absolute_url()


class TrackDeleteView(View):
    """Track dlete view to set is_deleted attribute to True"""

    def post (self, request, slug):
        track = Track.active_objects.get(slug=slug)
        track.is_deleted = True
        track.save()


# Student Views
class StudentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Student Create Form View to create one student at a time"""
    model = Student
    form_class = StudentCreationForm
    template_name = 'lms_admin/student_create.html'
    success_url = reverse_lazy('student_list')

    def form_valid(self, form):
        user, created = User.objects.get_or_create(email=form.cleaned_data['email'], 
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
        
        student = Student.objects.create(user=user, 
                                         cohort=form.cleaned_data['cohort'])
        
        subject = 'Account Setup Instructions' if created else 'Login Instructions'
        context = {
                    'first_name': user.first_name,
                    'set_password_url': self.get_password_reset_url(user) if created else self._get_login_url(student),
                }
        message = render_to_string('email_template.html', context)
        send_mail(subject, message, 'adebusolayeye.com', [user.email,])
        
        return super().form_valid(form)

    def get_password_reset_url(self, user):
        # Generate the password reset URL for the user
        token = default_token_generator.make_token(user) #generate token to ensure one time use of URL
        uid = urlsafe_base64_encode(force_bytes(user.pk)).decode() #encode user pk for security
        url = reverse('password_reset_confirm', args=[uid, token])
        return self.request.build_absolute_uri(url)

    def _get_login_url(self, student):
        if student.is_verified:
            return self.request.build_absolute_uri(reverse('login')) 


class StudentListView(ListView):
    """Generic Student List View to list all students"""
    model = Student
    template_name = 'lms_admin/student_list.html'
    context_object_name = 'students'

    def get_queryset(self):
            return Student.objects.all()


class StudentDetailView(DetailView):
    """Generic Student Detail View""" 
    model = Student 
    template_name = 'lms_admin/student_detail.html'
    context_object_name = 'student'


class StudentUpdateView(UpdateView):
    """Generic Student Update Form View"""
    model = Student
    form_class = StudentCreationForm
    template_name = 'lms_admin/student_update.html'
    
    def get_success_url(self):
        return self.object.get_absolute_url()


class StudentDeleteView(View):
    """Student Delete View to set is_deleted to True"""
    def post (self, request, id):
        student = Student.objects.get(id=id)
        student.is_deleted = True
        student.save()


class ToggleStudentSuspendView(View):

    def post(self, request, *args, **kwargs):
        student = get_object_or_404(Student, id=kwargs['pk'])
        student.is_suspended = not student.is_suspended
        student.save()


class StudentImportView(PasswordResetView, FormView):
    """Student Import View to create many students from a CSV file and send login/set password URLs in email"""
    template_name = 'import_students.html'
    form_class = StudentImportForm
    success_url = '/import/success/'

    def form_valid(self, form):
        students = form.process_csv()
        for student in students:
            email = student['email']
            first_name = student['first_name']
            last_name = student['last_name']
            cohort = student['cohort'] 

            user, created = User.objects.get_or_create(email=email,
                                                        first_name=first_name,
                                                        last_name=last_name)
            
            student = Student.objects.create(user=user, cohort=cohort)
            subject = 'Account Setup Instructions' if created else 'Login Instructions'
            context = {
                    'first_name': first_name,
                    'verification_url': self.get_password_reset_url(user) if created else self._get_login_url(student),
                }
            message = render_to_string('email_template.html', context)
            send_mail(subject, message, 'adebusolayeye.@gmailcom', [self.email,])
            
        return super().form_valid(form)

    def get_password_reset_url(self, user):
        # Generate the password reset URL for the user
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
        url = reverse('password_reset_confirm', args=[uid, token])
        return self.request.build_absolute_uri(url)

    def _get_login_url(self, student):
        if student.is_verified:
            return self.request.build_absolute_uri(reverse('login'))


# Cohort Views
class CohortCreateFormView(CreateView):
    """Generic Cohort Create View"""
    form_class = CohortCreateForm
    template_name = "admin/cohort_create_form.html"


class CohortListView(ListView):
    "Cohort List View to list all Cohorts"
    model = Cohort
    template_name = "admin/cohort_list.html"
    context_object_name = "cohort_list"

    def get_queryset(self):
        queryset = Cohort.objects.all()
        return queryset
    
  
    #Tutor Views 
class TutorCreateFormView(CreateView):
    form_class = TutorCreationForm
    template_name = "admin/tutor_create_form.html"
    success_url = reverse_lazy('tutor_list')

    def form_valid(self, form):
        user = User.objects.create_user(email=form.cleaned_data['email'], 
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
        
        tutor = Tutor.objects.create(user=user, 
                                    track=form.cleaned_data['track'])
        
        subject = 'Account Setup Instructions'
        context = {
                    'user': user,
                    'set_password_url': self.get_password_reset_url(user),
                }
        message = render_to_string('email_template.html', context)
        send_mail(subject, message, 'adebusolayeye@gmail.com', [user.email,])
        
        return super().form_valid(form)

    def get_password_reset_url(self, user):
        """ Generate the password reset URL for the user"""
        token = default_token_generator.make_token(user) # generate token to ensure one time use of URL
        uid = urlsafe_base64_encode(force_bytes(user.pk)).decode() # encode user pk for security
        url = reverse('password_reset_confirm', args=[uid, token])
        return self.request.build_absolute_uri(url)

    def _get_login_url(self, student):
        """Generate a login URL for existing users"""
        if student.is_verified:
            return self.request.build_absolute_uri(reverse('login')) 


class TutorListView(ListView):
    """Generic Tutor List View to view all Tutors"""
    model = Tutor
    template_name = "admin/tutor_list.html"
    context_object_name = 'tutor_list'

    def get_queryset(self):
        return Tutor.objects.all()


class TutorUpdateView(UpdateView):
    model = Tutor
    template_name = "admin/tutor_update_form.html"
    fields = "__all__"

    def form_valid(self, form):
        return super().form_valid(form)
    

class TutorDetailView(DetailView):
    model = Tutor
    template_name = "admin/tutor_detail.html"


class TutorDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    
    def post(self, request, *args, **kwargs):
        tutor = get_object_or_404(Tutor, id=kwargs['pk'])
        tutor.is_deleted = True
        tutor.save() 


class ToggleTutorSuspendView(View):

    def post(self, request, *args, **kwargs):
        tutor = get_object_or_404(Tutor, id=kwargs['pk'])
        tutor.is_suspended = not tutor.is_suspended
        tutor.save()


# Applicant Views
class ApplicantCreateView(CreateView):
    form_class = ApplicantForm
    template_name = "admin/application_form"
    success_url = reverse_lazy('home_page')

    def form_valid(self, form):
        applicant = form.save(commit=False)
        applicant.cohort = Cohort.objects.get(year=timezone.now().year)
        applicant.save()
        return super().form_valid(form)


class ApplicantApprovalFormView(View):
    template_name = 'applicant_checklist.html'

    def get(self, request):
        form = ApplicantChecklistForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ApplicantChecklistForm(request.POST)
        if form.is_valid():
            selected_applicants = form.cleaned_data['applicants']
            for applicant in selected_applicants:
                applicant.is_approved = True
                applicant.save()
            messages.success(request, "Applicants have been approved successfully.")
            return HttpResponseRedirect(reverse("lms_admin:export_to_csv"))
        return render(request, self.template_name, {'form': form})


class ExportApprovedApplicantsCSVView(View):

    def get(self, request):
        # Filter approved applicants using ApprovedApplicantManager and filter for only current cohort
        approved_applicants = Applicant.approved.filter(cohort=Cohort.objects.get(year=timezone.now().year))

        # Create CSV file
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="approved_applicants.csv"'

        writer = csv.writer(response)
        writer.writerow(['First Name', 'Last Name', 'Email'])

        for applicant in approved_applicants:
            writer.writerow([applicant.first_name, applicant.last_name, applicant.email])

        return response