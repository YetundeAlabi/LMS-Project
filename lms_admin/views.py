import csv
from typing import Any, Dict

from accounts.forms import StudentForm, TutorForm
from accounts.models import Student, Tutor, User
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View
from django.views.generic import (CreateView, DeleteView, DetailView, FormView,
                                  ListView, TemplateView, UpdateView)
from lms_admin.forms import (ApplicantChecklistForm, ApplicantForm,
                             CohortCreateForm, StudentImportForm, TrackForm)
from lms_admin.models import Track
from tutor.studentcadd import register_courses

from .models import Applicant, Cohort
from .tasks import send_verification_mail

# Create your views here

class AdminUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class DashboardView(LoginRequiredMixin, AdminUserRequiredMixin, TemplateView): 
    template_name = "lms_admin/dashboard3.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_year = timezone.now().year
        context['students'] = Student.objects.all()
        context['tutors'] = Tutor.objects.all()
        context['tracks'] = Track.active_objects.all()
        context['cohort'] = Cohort.objects.get(year=current_year)
        context['applicants'] = Applicant.objects.all()
        context['male_applicants'] = Applicant.objects.filter(
            gender='M', cohort__year=current_year).count()
        context['female_applicants'] =  Applicant.objects.filter(gender='F', cohort__year=current_year).count()
        return context


# Track Views
class TrackCreateView(LoginRequiredMixin, AdminUserRequiredMixin, CreateView):
    """Track Create View"""
    model = Track
    form_class = TrackForm
    template_name = 'lms_admin/track_create.html'
    success_url = reverse_lazy('lms_admin:track_list')

    def form_valid(self, form):
        messages.success(self.request, "Track created successfully")
        return super().form_valid(form)
    

class TrackListView(LoginRequiredMixin, AdminUserRequiredMixin, ListView):
    """Track List View to list all active Tracks"""
    model = Track
    template_name = 'lms_admin/track_list1.html'
    context_object_name = 'tracks'

    def get_queryset(self):
            return Track.active_objects.all()
    

class TrackDetailView(LoginRequiredMixin, AdminUserRequiredMixin, DetailView): 
    """Generic Track Detail View"""
    model = Track 
    template_name = 'lms_admin/track_detail.html'
    context_object_name = 'track'
    slug_url_kwarg = 'slug'
    slug_field = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['track_students'] = Student.objects.filter(track=self.object)
        return context


class TrackUpdateView(LoginRequiredMixin, AdminUserRequiredMixin, UpdateView):
    """Generic Track Update View"""
    model = Track
    form_class = TrackForm
    template_name = 'lms_admin/track_update.html'
    slug_url_kwarg = 'slug'
    slug_field = 'slug'
    
    def form_valid(self, form):
        messages.success(self.request, "Track information has been updated successfully")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


class TrackConfirmDeleteView(LoginRequiredMixin, AdminUserRequiredMixin,TemplateView):
    template_name = "lms_admin/track_confirm_delete.html"
    slug_url_kwarg = 'slug'
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['track'] = Track.objects.get(slug=self.kwargs['slug'])
        return context 


# Student Views
class StudentCreateView(LoginRequiredMixin, AdminUserRequiredMixin, CreateView):
    """Student Create Form View to create one student at a time"""
    form_class = StudentForm
    template_name = 'lms_admin/student_create.html'
    success_url = reverse_lazy('student_list')

    def form_valid(self, form):
        
        email=form.cleaned_data.get('email') 
        first_name=form.cleaned_data.get('first_name')
        last_name=form.cleaned_data.get('last_name') 
        cohort=form.cleaned_data.get('cohort')
        track=form.cleaned_data.get('track')
        gender=form.cleaned_data.get('gender')
        picture=form.cleaned_data.get('picture')
        phone_number=form.cleaned_data.get('phone_number')
        address=form.cleaned_data.get('address')
        

        user, created = User.objects.get_or_create(email=email, 
                                                    first_name=first_name, 
                                                    last_name=last_name)
        student = Student.objects.create(user=user, cohort=cohort, track=track, 
                                            gender=gender, picture=picture, 
                                            phone_number=phone_number, address=address)
        
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


class StudentListView(LoginRequiredMixin, AdminUserRequiredMixin, ListView):
    """Generic Student List View to list all students"""
    model = Student
    template_name = 'lms_admin/student_list.html'
    context_object_name = 'students'

    def get_queryset(self):
        return Student.active_objects.all()


class StudentDetailView(LoginRequiredMixin, AdminUserRequiredMixin, DetailView):
    """Generic Student Detail View""" 
    model = Student 
    template_name = 'lms_admin/student_detail.html'
    context_object_name = 'student'


class StudentUpdateView(LoginRequiredMixin, AdminUserRequiredMixin, UpdateView):
    """Generic Student Update Form View"""
    form_class = StudentForm
    template_name = 'lms_admin/student_update.html'
    model = Student

    # def get_object(self, queryset=None):
    #     return Student.objects.get(pk= self.kwargs["pk"])

    def get_initial(self):
        initial = super().get_initial()
        student = self.get_object()
        initial['first_name'] = student.user.first_name
        initial['last_name'] = student.user.last_name
        initial['email'] = student.user.email
        return initial

    def form_valid(self, form):
        student = self.get_object()
        student.cohort = form.cleaned_data['cohort']
        student.track = form.cleaned_data['track']
        student.gender = form.cleaned_data['gender']
        student.picture = form.cleaned_data['picture']
        student.user.first_name = form.cleaned_data['first_name']
        student.user.last_name = form.cleaned_data['last_name']
        student.user.email = form.cleaned_data['email']
        student.user.save()
        student.save()
        messages.success(self.request, "Student information updated successfully")
        return HttpResponseRedirect(reverse('lms_admin:student_list'))
    

class StudentDeleteView(LoginRequiredMixin, AdminUserRequiredMixin, DeleteView):
    model = Student
    template_name = 'lms_admin/student_delete_confirm.html'
    success_url = reverse_lazy('lms_admin:student_list')


class ToggleStudentSuspendView(LoginRequiredMixin,  AdminUserRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        student = get_object_or_404(Student, id=kwargs['pk'])
        student.is_suspended = not student.is_suspended
        student.save(update_fields=['is_suspended'])
        if student.is_suspended:
            messages.warning(self.request, f"{student.user.first_name} has been suspended successfully")
        else:
            messages.success(self.request, f"Suspension has been lifted for {student.user.first_name}")
        return HttpResponseRedirect(reverse('lms_admin:student_list'))


class StudentImportView(PasswordResetView, AdminUserRequiredMixin, FormView):
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
            phone_number = student['phone_number']
            address = student['address']

            user, created = User.objects.get_or_create(email=email,
                                                        first_name=first_name,
                                                        last_name=last_name)
            print(track)
            track_obj = Track.active_objects.get(name=track.strip())
            student = Student.objects.create(user=user, cohort=cohort, gender=gender, track=track_obj,
                                             phone_number=phone_number, address=address)
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
class CohortCreateFormView(LoginRequiredMixin, AdminUserRequiredMixin, CreateView):
    """Generic Cohort Create View"""
    form_class = CohortCreateForm
    template_name = "lms_admin/cohort_create_form.html"
    success_url = reverse_lazy('lms_admin:cohort_list')

    def form_valid(self, form):
        messages.success(self.request, "Cohort created successfully")
        return super().form_valid(form)
    

class CohortListView(LoginRequiredMixin, AdminUserRequiredMixin, ListView):
    "Cohort List View to list all Cohorts"
    model = Cohort
    template_name = "admin/cohort_list.html"
    context_object_name = "cohorts"

    def get_queryset(self):
        queryset = Cohort.objects.all()
        return queryset


class CohortDetailView(LoginRequiredMixin, AdminUserRequiredMixin, DetailView): 
    model = Cohort
    template_name = 'lms_admin/cohort_detail.html'
    context_object_name = 'cohort'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cohort_students'] = Student.objects.filter(cohort=self.object)
        return context

    
#Tutor Views 
class TutorCreateFormView(LoginRequiredMixin, AdminUserRequiredMixin, CreateView): #PermissionRequiredMixin,
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


class TutorListView(LoginRequiredMixin, AdminUserRequiredMixin, ListView): #PermissionRequiredMixin,
    """Generic Tutor List View to view all Tutors"""
    model = Tutor
    template_name = "lms_admin/tutor_list.html"
    context_object_name = 'tutors'

    def get_queryset(self):
        return Tutor.active_objects.all()


class TutorUpdateView(LoginRequiredMixin, AdminUserRequiredMixin, UpdateView): #PermissionRequiredMixin,
    form_class = TutorForm
    model = Tutor
    template_name = "lms_admin/tutor_update_form.html"
    
    # def get_object(self, queryset=None):
    #     return Tutor.objects.get(pk= self.kwargs["pk"])

    def get_initial(self):
        initial = super().get_initial()
        tutor = self.get_object()
        initial['track'] = tutor.track
        initial['first_name'] = tutor.user.first_name
        initial['last_name'] = tutor.user.last_name
        initial['email'] = tutor.user.email
        return initial
     
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
        
    
class TutorDetailView(LoginRequiredMixin, AdminUserRequiredMixin, DetailView):
    model = Tutor
    template_name = "lms_admin/tutor_detail.html"

class TutorConfirmDeleteView(LoginRequiredMixin, AdminUserRequiredMixin,TemplateView):
    template_name = "lms_admin/tutor_confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tutor'] = Tutor.objects.get(pk=self.kwargs['pk'])
        return context 


class TutorDeleteView(LoginRequiredMixin, AdminUserRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        tutor = get_object_or_404(Tutor, pk=kwargs['pk'])
        tutor.is_deleted = True
        tutor.save(update_fields=['is_deleted']) 
        return HttpResponseRedirect(reverse('lms_admin:tutor_list'))


class ToggleTutorSuspendView(LoginRequiredMixin, AdminUserRequiredMixin, View): #PermissionRequiredMixin,
    def post(self, request, *args, **kwargs):
        tutor = get_object_or_404(Tutor, pk=kwargs['pk'])
        tutor.is_suspended = not tutor.is_suspended
        tutor.save(update_fields=['is_suspended'])
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


class ApplicantApprovalFormView(LoginRequiredMixin, AdminUserRequiredMixin, View):
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
    
    
class AllApplicantListView(LoginRequiredMixin, AdminUserRequiredMixin, ListView):
    model = Applicant
    template_name = 'lms_admin/all_applicants.html'
    context_object_name = 'applicants'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        unapproved_count = self.object_list.filter(is_approved=False).count()
        context['unapproved_count'] = unapproved_count
        return context


class ApplicantListView(LoginRequiredMixin, AdminUserRequiredMixin, ListView):
    model = Applicant
    template_name = 'lms_admin/applicant_list.html'
    context_object_name = 'applicants'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_approved=False)
        return queryset



class ExportApprovedApplicantsCSVView(LoginRequiredMixin, AdminUserRequiredMixin, View):
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