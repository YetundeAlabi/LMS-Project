<<<<<<< HEAD
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, UpdateView, TemplateView
from lms_admin.models import Track
from lms_admin.forms import TrackForm
from accounts.models import Student
from accounts.forms import StudentCreationForm
import csv
from django.shortcuts import render
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from django.views import View
from .forms import StudentImportForm
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

    def get_queryset(self):
            return Track.active_objects.all()
    

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

    def get_queryset(self):
            return Student.objects.all()


class StudentDetailView(DetailView, LoginRequiredMixin, PermissionRequiredMixin): 
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


from django.views.generic import FormView
from django.core.mail import send_mail
from .forms import StudentImportForm
from accounts.models import Student

class StudentImportView(FormView):
    template_name = 'import_students.html'
    form_class = StudentImportForm
    success_url = '/import/success/'

    def form_valid(self, form):
        students = form.process_csv()
        for student in students:
            username = student['username']
            email = student['email']
            is_verified = student['is_verified']
            is_suspended = student['is_suspended']
            is_deleted = student['is_deleted']

            student, created = Student.objects.get_or_create(
                username=username,
                email=email,
                defaults={
                    'is_verified': is_verified,
                    'is_suspended': is_suspended,
                    'is_deleted': is_deleted
                }
            )

            if created:
                subject = 'Login Instructions' if is_verified else 'Account Setup'
                context = {
                    'username': username,
                    'verification_url': self._get_verification_url(student),
                    'login_url': self._get_login_url(student),
                }
                message = render_to_string('email_template.html', context)
                send_mail(subject, message, 'sender@example.com', [email])

        return super().form_valid(form)

    def _get_verification_url(self, student):
            return self.request.build_absolute_uri(reverse('account_setup', args=[student.id]))

    def _get_login_url(self, student):
        if student.is_verified:
            return self.request.build_absolute_uri(reverse('login'))


from accounts.models import Tutor

from .models import Cohort
from .forms import CohortCreateForm


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
        suspension_status = tutor.is_suspended
        tutor.is_suspended = not suspension_status
        tutor.save()
=======
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
        tutor = get_object_or_404(Tutor, id=kwargs['pk'])
        tutor.is_deleted = True
        tutor.save() 


class ToggleTutorSuspendView(LoginRequiredMixin, PermissionRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        tutor = get_object_or_404(Tutor, id=kwargs['pk'])
        suspension_status = tutor.is_suspended
        tutor.is_suspended = not suspension_status
        tutor.save()
>>>>>>> 1568624f1dded75260be81e8b19d4d847485d4ca
