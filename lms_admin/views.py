import csv
from typing import Any, Dict, Optional, Type

from django.contrib import messages
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import IntegrityError, models
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template, render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View
from django.views.generic import (
    CreateView, DetailView, FormView, ListView, UpdateView, TemplateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from tutor.studentcadd import register_courses
from accounts.forms import StudentCreationForm, TutorForm, TutorUpdateForm, StudentUpdateForm
from accounts.models import Student, Tutor, User
from lms_admin.forms import (
                            TrackForm, CohortCreateForm, StudentImportForm,ApplicantChecklistForm, ApplicantForm)
from lms_admin.models import Track
from .models import Applicant, Cohort
from .tasks import send_verification_mail
from base.constants import FEMALE, MALE

# Create your views here

class DashboardView(LoginRequiredMixin, TemplateView): 
    template_name = "lms_admin/dashboard3.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_year = timezone.now().year
        context['students'] = Student.objects.all()
        context['tutors'] = Tutor.objects.all()
        context['tracks'] = Track.objects.all()
        context['cohort'] = Cohort.objects.last()
        context['applicants'] = Applicant.objects.all()
        context['male_applicants'] = Applicant.objects.filter(
            gender='M', cohort__year=current_year).count()
        context['female_applicants'] =  Applicant.objects.filter(gender='F').count()
        return context


# Track Views
class TrackCreateView(LoginRequiredMixin, CreateView):
    """Track Create View"""
    model = Track
    form_class = TrackForm
    template_name = 'lms_admin/track_create.html'
    success_url = reverse_lazy('lms_admin:track_list')

    def save(self, *args, **kwargs):
        # Move to the form
        if not self.pk:
            if Track.active_objects.filter(name=self.name).exists():
                raise ValidationError('A track with the same name already exists.')
        super().save(*args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Track created successfully")
        return super().form_valid(form)
    

class TrackListView(LoginRequiredMixin, ListView):
    """Track List View to list all active Tracks"""
    model = Track
    template_name = 'lms_admin/track_list1.html'
    context_object_name = 'tracks'

    def get_queryset(self):
            return Track.active_objects.all()
    

class TrackDetailView(LoginRequiredMixin, DetailView): 
    """Generic Track Detail View"""
    model = Track 
    template_name = 'lms_admin/track_detail.html'
    context_object_name = 'track'
    slug_url_kwarg = 'slug'
    slug_field = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['track_students'] = Student.objects.filter(track=self.get_object())
        return context


class TrackUpdateView(LoginRequiredMixin, UpdateView):
    """Generic Track Update View"""
    model = Track
    form_class = TrackForm
    template_name = 'lms_admin/track_update.html'
    slug_url_kwarg = 'slug'
    slug_field = 'slug'
    
    def get_object(self, queryset=None):
        return Track.objects.get(slug=self.kwargs['slug'])
    
    def form_valid(self, form):
        messages.success(self.request, "Track information has been updated successfully")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


class TrackConfirmDeleteView(TemplateView):
    template_name = "lms_admin/track_confirm_delete.html"
    slug_url_kwarg = 'slug'
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['track'] = Track.objects.get(slug=self.kwargs['slug'])
        return context 


# Student Views
class StudentCreateView(LoginRequiredMixin, CreateView):
    """Student Create Form View to create one student at a time"""
    model = Student
    form_class = StudentCreationForm
    template_name = 'lms_admin/student_create.html'
    success_url = reverse_lazy('student_list')

    def form_valid(self, form):
        student, created = form.save()
        user = student.user
        self.object = student

        register_courses(self.object)
        
        subject = 'Login Instructions' if not created else  'Account Setup Instructions'
        context = {
                  'user': user,
                  'set_password_url': self.get_login_url() if not created else self.get_password_reset_url(user),
               }
        message = get_template('lms_admin/email_template.html').render(context)
        recipient = [user.email,]
        send_verification_mail.delay(subject, recipient, message)
        messages.success(self.request, "Student has been created successfully")
        return HttpResponseRedirect(reverse('lms_admin:student_list'))

    def get_password_reset_url(self, user):
        # Generate the password reset URL for the user
        token = default_token_generator.make_token(user) #generate token to ensure one time use of URL
        uid = urlsafe_base64_encode(force_bytes(user.pk)) #encode user pk for security
        url = reverse('accounts:set_password', args=[uid, token])
        return self.request.build_absolute_uri(url)

    def get_login_url(self):
        return self.request.build_absolute_uri(reverse('accounts:login')) 


class StudentListView(LoginRequiredMixin, ListView):
    """Generic Student List View to list all students"""
    model = Student
    template_name = 'lms_admin/student_list.html'
    context_object_name = 'students'

    def get_queryset(self):
        return Student.objects.all()


class StudentDetailView(LoginRequiredMixin, DetailView):
    """Generic Student Detail View""" 
    model = Student 
    template_name = 'lms_admin/student_detail.html'
    context_object_name = 'student'


class StudentUpdateView(LoginRequiredMixin, UpdateView):
    """Generic Student Update Form View"""
    model = Student
    form_class = StudentUpdateForm
    template_name = 'lms_admin/student_update.html'

    def get_object(self, queryset=None):
        return Student.objects.get(pk= self.kwargs["pk"])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        form.initial = self.get_initial()
        form.fields['first_name'].initial = self.object.user.first_name
        form.fields['last_name'].initial = self.object.user.last_name
        form.fields['email'].initial = self.object.user.email
        form.fields['gender'].initial = self.object.gender
        form.fields['track'].initial = self.object.track
        form.fields['picture'].initial = self.object.picture

        return self.render_to_response(self.get_context_data(form=form))
        
    def form_valid(self, form):
        student = self.get_object()
        student.track = form.cleaned_data['track']
        student.gender = form.cleaned_data['gender']
        student.picture = form.cleaned_data['picture']
        student.user.first_name = form.cleaned_data['first_name']
        student.user.last_name = form.cleaned_data['last_name']
        student.user.email = form.cleaned_data['email']
        student.user.save()
        student.save()
        messages.success(self.request, "Student information updated successfully")
        return HttpResponseRedirect(reverse('lms_admin:student_detail', kwargs={'pk': student.pk}))
    

class StudentDeleteView( LoginRequiredMixin, DeleteView):
    model = Student
    template_name = 'lms_admin/student_delete_confirm.html'
    success_url = reverse_lazy('lms_admin:student_list')


class ToggleStudentSuspendView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        student = get_object_or_404(Student, id=kwargs['pk'])
        student.is_suspended = not student.is_suspended
        student.save(update_fields=['is_suspended'])
        return HttpResponseRedirect(reverse('lms_admin:student_list'))


class StudentImportView(PasswordResetView, FormView):
    """Student Import View to create many students from a CSV file and send login/set password URLs in email"""
    template_name = 'lms_admin/import_students.html'
    form_class = StudentImportForm
    success_url = '/import/success/'

    def form_valid(self, form):
        students = form.process_csv()
        for student in students:
            email = student['email']
            first_name = student['first_name']
            last_name = student['last_name']
            cohort = student['cohort'] 
            gender = student['gender']
            track = student['track']

            user, created = User.objects.get_or_create(email=email,
                                                        first_name=first_name,
                                                        last_name=last_name)
            print(track)
            track_obj = Track.active_objects.get(name=track.strip())
            student = Student.objects.create(user=user, cohort=cohort, gender=gender, track=track_obj)
            subject = 'Account Setup Instructions' if created else 'Login Instructions'
            context = {
                    'first_name': first_name,
                    'verification_url': self.get_password_reset_url(user) if created else self._get_login_url(),
               }
        message = get_template('lms_admin/email_template.html').render(context)
        recipient = [user.email,]
        send_verification_mail.delay(subject, recipient, message)
        messages.success(self.request, "Multiple students created successfully")
        return HttpResponseRedirect(reverse('lms_admin:student_list'))  
    
    def get_password_reset_url(self, user):
        # Generate the password reset URL for the user
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        url = reverse('accounts:set_password', args=[uid, token])
        return self.request.build_absolute_uri(url)

    def _get_login_url(self):
        return self.request.build_absolute_uri(reverse('accounts:login'))


# Cohort Views
class CohortCreateFormView(LoginRequiredMixin, CreateView):
    """Generic Cohort Create View"""
    form_class = CohortCreateForm
    template_name = "lms_admin/cohort_create_form.html"
    success_url = reverse_lazy('lms_admin:cohort_list')

    def form_valid(self, form):
        messages.success(self.request, "Cohort created successfully")
        return super().form_valid(form)
    

class CohortListView(LoginRequiredMixin, ListView):
    "Cohort List View to list all Cohorts"
    model = Cohort
    template_name = "admin/cohort_list.html"
    context_object_name = "cohorts"

    def get_queryset(self):
        queryset = Cohort.objects.all()
        return queryset


class CohortDetailView(LoginRequiredMixin, DetailView): 
    model = Cohort
    template_name = 'lms_admin/cohort_detail.html'
    context_object_name = 'cohort'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cohort_students'] = Student.objects.filter(cohort=self.object)
        return context

    
#Tutor Views 
class TutorCreateFormView(LoginRequiredMixin, CreateView): #PermissionRequiredMixin,
    form_class = TutorForm
    template_name = "lms_admin/tutor_create_form.html"
    success_url = reverse_lazy('lms_admin:tutor_list')

    def form_valid(self, form):
        track = form.cleaned_data.get("track")
        email = form.cleaned_data.get('email')
        first_name = form.cleaned_data.get('first_name')
        last_name= form.cleaned_data.get('last_name')
        user = User.objects.create_user(email=email, 
                                        first_name=first_name, 
                                        last_name=last_name)
        tutor = Tutor.objects.create(user=user, track=track)
        self.object = tutor
        subject = 'Account Setup Instructions'
        context = {
                    'user': user,
                    'set_password_url': self.get_password_reset_url(user),
                }
        message = get_template('lms_admin/email_template.html').render(context)
        recipient = [user.email,]
        send_verification_mail.delay(subject, recipient, message)
        messages.success(self.request, "Tutor created successfully")
        return HttpResponseRedirect(reverse('lms_admin:tutor_list'))

    def get_password_reset_url(self, user):
        """ Generate the password reset URL for the user"""
        token = default_token_generator.make_token(user) # generate token to ensure one time use of URL
        uid = urlsafe_base64_encode(force_bytes(user.pk)) # encode user pk for security
        url = reverse('accounts:set_password', args=[uid, token])
        return self.request.build_absolute_uri(url)


class TutorListView(LoginRequiredMixin,  ListView): #PermissionRequiredMixin,
    """Generic Tutor List View to view all Tutors"""
    model = Tutor
    template_name = "lms_admin/tutor_list.html"
    context_object_name = 'tutors'

    def get_queryset(self):
        return Tutor.objects.all()


class TutorUpdateView(LoginRequiredMixin, UpdateView): #PermissionRequiredMixin,
    form_class = TutorForm
    template_name = "lms_admin/tutor_update_form.html"
    
    def get_object(self, queryset=None):
        return Tutor.objects.get(pk= self.kwargs["pk"])
     
    def form_valid(self, form):
        tutor = self.get_object()
        tutor.track = form.cleaned_data['track']
        tutor.user.first_name = form.cleaned_data['first_name']
        tutor.user.last_name = form.cleaned_data['last_name']
        tutor.user.email = form.cleaned_data['email']
        tutor.user.save()
        tutor.save()
        messages.success(self.request, "Tutor information updated successfully")
        return HttpResponseRedirect(reverse('lms_admin:tutor_list'))
        
    
class TutorDetailView(DetailView):
    model = Tutor
    template_name = "lms_admin/tutor_detail.html"


class TutorDeleteView(LoginRequiredMixin, View):
    
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
        if tutor.is_suspended:
            messages.success(self.request, f"{tutor.user.first_name} has been suspended successfully")
            return HttpResponseRedirect(reverse('lms_admin:tutor_list'))
        messages.success(self.request, f"Suspension has been lifted for {tutor.user.first_name}")
        return HttpResponseRedirect(reverse('lms_admin:tutor_list'))


# Applicant Views
class ApplicantCreateView(CreateView):
    form_class = ApplicantForm
    template_name = "lms_admin/application_form2.html"
    success_url = reverse_lazy('lms_admin:applicant_thank_you')

    def form_valid(self, form):
        applicant = form.save(commit=False)
        applicant.cohort = Cohort.objects.get(year=timezone.now().year)
        applicant.save()
        # messages.success(self.request, "Thank you for applying. Your application has been submitted successfully.")
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
            return HttpResponseRedirect(reverse("lms_admin:all_applicant"))
        return render(request, self.template_name, {'form': form})
    
    
class AllApplicantListView(ListView):
    model = Applicant
    template_name = 'lms_admin/all_applicants.html'
    context_object_name = 'applicants'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        unapproved_count = self.object_list.filter(is_approved=False).count()
        context['unapproved_count'] = unapproved_count
        return context


class ApplicantListView(ListView):
    model = Applicant
    template_name = 'lms_admin/applicant_list.html'
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