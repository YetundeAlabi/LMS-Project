import csv

from typing import Any, Dict, Optional, Type
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView
from django.core.mail import send_mail
from django.db import models
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

from accounts.forms import StudentCreationForm, TutorCreationForm, TutorUpdateForm
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
    form_class = TrackForm
    template_name = 'lms_admin/track_create.html'
    success_url = reverse_lazy('lms_admin:track_list')

    def form_valid(self, form):
        messages.success(self.request, "Track created successfully")
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
        return context


class TrackUpdateView(UpdateView):
    """Generic Track Update View"""
    form_class = TrackForm
    template_name = 'lms_admin/track_create.html'
    slug_url_kwarg = 'slug'
    slug_field = 'slug'
    queryset = Track.active_objects.all()
    
    def get_object(self, queryset=None):
        return Track.objects.get(slug=self.kwargs['slug'])

    def get_success_url(self):
        return self.object.get_absolute_url()


class TrackDeleteView(View):
    """Track delete view to set is_deleted attribute to True"""

    def get(self, request, slug):
        track = Track.active_objects.get(slug=slug)
        track.is_deleted = True
        track.save()
        return HttpResponseRedirect(reverse("lms_admin:track_list"))


# Student Views
class StudentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Student Create Form View to create one student at a time"""
    model = Student
    form = StudentCreationForm
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
        send_mail(subject, message, 'adeosunfaith0101@gmail.com', [user.email,])
        
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


class StudentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Generic Student List View to list all students"""
    model = Student
    template_name = 'lms_admin/student_list.html'
    context_object_name = 'students'

    def get_queryset(self):
            return Student.objects.all()


class StudentDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """Generic Student Detail View""" 
    model = Student 
    template_name = 'lms_admin/student_detail.html'
    context_object_name = 'student'


class StudentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Generic Student Update Form View"""
    model = Student
    form = StudentCreationForm
    template_name = 'lms_admin/student_update.html'
    
    def get_success_url(self):
        return self.object.get_absolute_url()


class StudentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Student Delete View to set is_deleted to True"""
    def post (self, request, id):
        student = Student.objects.get(id=id)
        student.is_deleted = True
        student.save()


class ToggleStudentSuspendView(LoginRequiredMixin, PermissionRequiredMixin, View):

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
            send_mail(subject, message, 'adeosunfaith0101@gmail.com', [email,])
            
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
class CohortCreateFormView(LoginRequiredMixin,PermissionRequiredMixin, CreateView):
    """Generic Cohort Create View"""
    form_class = CohortCreateForm
    template_name = "admin/cohort_create_form.html"


class CohortListView(LoginRequiredMixin, PermissionRequiredMixin, ListView): 
    "Cohort List View to list all Cohorts"
    model = Cohort
    template_name = "admin/cohort_list.html"
    context_object_name = "cohort_list"

    def get_queryset(self):
        queryset = Cohort.objects.all()
        return queryset
    
  
    #Tutor Views 
class TutorCreateFormView(LoginRequiredMixin, CreateView): #PermissionRequiredMixin,
    form_class = TutorCreationForm
    template_name = "lms_admin/tutor_create_form.html"
    success_url = reverse_lazy('lms_admin:tutor_list')

    def form_valid(self, form):
        tutor = form.save()
        user = tutor.user
        self.object = tutor
        return HttpResponseRedirect(reverse('lms_admin:tutor_list'))
    
        # return super().form_valid()
        

        # user = User.objects.create_user(email=form.cleaned_data['email'], 
        #                                 first_name=form.cleaned_data['first_name'],
        #                                 last_name=form.cleaned_data['last_name'])
        
        # tutor = Tutor.objects.create(user=user, 
        #                             track=form.cleaned_data['track'])
        # tutor.save()
        # subject = 'Account Setup Instructions'
        # context = {
        #             'user': user,
        #             'set_password_url': self.get_password_reset_url(user),
        #         }
        # message = render_to_string('email_template.html', context)
        # send_mail(subject, message, 'adeosunfaith0101@gmail.com', [user.email,])
        
        # return super().form_valid(form)
    

    def get_password_reset_url(self, user):
        """ Generate the password reset URL for the user"""
        token = default_token_generator.make_token(user) # generate token to ensure one time use of URL
        uid = urlsafe_base64_encode(force_bytes(user.pk)).decode() # encode user pk for security
        url = reverse('password_reset_confirm', args=[uid, token])
        return self.request.build_absolute_uri(url)

    def _get_login_url(self, tutor):
        """Generate a login URL for existing users"""
        if tutor.is_verified:
            return self.request.build_absolute_uri(reverse('login')) 


class TutorListView(LoginRequiredMixin,  ListView): #PermissionRequiredMixin,
    """Generic Tutor List View to view all Tutors"""
    model = Tutor
    template_name = "lms_admin/tutor_list.html"
    context_object_name = 'tutors'

    def get_queryset(self):
        return Tutor.objects.all()


class TutorUpdateView(LoginRequiredMixin, UpdateView): #PermissionRequiredMixin,
    model = Tutor
    form_class = TutorUpdateForm
    template_name = "lms_admin/tutor_update_form.html"
    
    def get_object(self, queryset=None):
        return Tutor.objects.get(pk= self.kwargs["pk"])
        
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        form.initial = self.get_initial()
        form.fields['first_name'].initial = self.object.user.first_name
        form.fields['last_name'].initial = self.object.user.last_name
        form.fields['email'].initial = self.object.user.email
        form.fields['track'].initial = self.object.track

        return self.render_to_response(self.get_context_data(form=form))
        
    def form_valid(self, form):
        tutor = self.get_object()
        tutor.track = form.cleaned_data['track']
        tutor.user.first_name = form.cleaned_data['first_name']
        tutor.user.last_name = form.cleaned_data['last_name']
        tutor.user.email = form.cleaned_data['email']
        tutor.user.save()
        tutor.save()
        return HttpResponseRedirect(reverse('lms_admin:tutor_list'))
        
    
class TutorDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Tutor
    template_name = "lms_admin/tutor_detail.html"


class TutorDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    
    def get(self, request, *args, **kwargs):
        tutor = get_object_or_404(Tutor, id=kwargs['pk'])
        tutor.is_deleted = True
        tutor.save() 
        return HttpResponseRedirect(reverse('lms_admin:tutor_list'))


class ToggleTutorSuspendView(LoginRequiredMixin, View): #PermissionRequiredMixin,

    def get(self, request, *args, **kwargs):
        tutor = get_object_or_404(Tutor, pk=kwargs['pk'])
        tutor.is_suspended = not tutor.is_suspended
        tutor.save()
        return HttpResponseRedirect(reverse('lms_admin:tutor_list'))


# Applicant Views
class ApplicantCreateView(CreateView):
    form_class = ApplicantForm
    template_name = "lms_admin/application_form.html"
    success_url = reverse_lazy('lms_admin:applicant_thank_you')

    def form_valid(self, form):
        applicant = form.save(commit=False)
        applicant.cohort = Cohort.objects.get(year=timezone.now().year)
        applicant.save()
        messages.success(self.request, "Thank you for applying. Your application has been submitted successfully.")
        return super().form_valid(form)
    

class ApplicantThankYouView(View):
    template_name = "lms_admin/applicant_thank_you.html"

    def get(self, request):
        return render(request, self.template_name)


class ApplicantApprovalFormView(LoginRequiredMixin, View):
    template_name = 'lms_admin/applicant_checklist.html'

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
            return HttpResponseRedirect(reverse("lms_admin:applicant_list"))
        return render(request, self.template_name, {'form': form})


class ApplicantListView(ListView):
    model = Applicant
    template_name = 'applicant_list.html'
    context_object_name = 'applicants'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_approved=False)
        return queryset


class ExportApprovedApplicantsCSVView(View):

    def get(self, request):
        # Filter approved applicants using ApprovedApplicantManager and filter for only current cohort
        approved_applicants = Applicant.approved.filter(cohort=Cohort.objects.get(year=timezone.now().year))

        # Create CSV file
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="approved_applicants.csv"'

        writer = csv.writer(response)
        writer.writerow(['First Name', 'Last Name', 'Email', 'Gender', 'Track'])

        for applicant in approved_applicants:
            writer.writerow([applicant.first_name, applicant.last_name, applicant.email, applicant.gender, applicant.track])
    
        return response