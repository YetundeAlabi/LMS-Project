from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth import (authenticate, get_user_model, login, logout,
                                 views)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView, PasswordChangeView
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View, generic
from django.views.generic import CreateView
from django.views.generic.edit import UpdateView

from .forms import (LoginForm, SignUpForm, StudentUpdateForm, TutorUpdateForm,
                    UserForm)
from .models import Student, Tutor, User

# Create your views here.

User = get_user_model()

class TutorSignUpView(CreateView):
    model = Tutor
    form_class = UserForm
    template_name = 'accounts/signup.html' 
    success_url = reverse_lazy('login')

class SignOutView(LogoutView):
    next_page = reverse_lazy('accounts:login')

class LoginView(generic.FormView):
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        user = authenticate(email=email, password=password)
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        messages.error(self.request, "Invalid email or password")
        return super().form_invalid(form)

    def get_success_url(self) -> str:
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff:
                return reverse('lms_admin:dashboard')
            elif hasattr(user, "tutor"):
                return reverse('course:tutor_dashboard_view')
            else:
                return reverse('home_page')
        return reverse('login')
        
            
class ChangePasswordView(PasswordChangeView):
    template_name = 'accounts/change_password.html'  
    success_url = reverse_lazy('login')


class TutorUpdateView(LoginRequiredMixin, UpdateView):
    model = Tutor
    form_class = TutorUpdateForm
    template_name = 'update_profile.html'
    success_url = reverse_lazy('tutor-home')

    def get_object(self, queryset=None):
        tutor_id = self.kwargs.get('tutor_id')
        return get_object_or_404(self.model, pk=tutor_id)

    def form_valid(self, form):
        response = super().form_valid(form)
        tutor_id = self.kwargs.get('tutor_id')
        return redirect('tutor_detail', tutor_id=tutor_id)
    

class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentUpdateForm
    template_name = 'update_profile.html'
    success_url = reverse_lazy('student-home')

    def get_object(self, queryset=None):
        student_id = self.kwargs.get('student_id')
        return get_object_or_404(self.model, pk=student_id)

    def form_valid(self, form):
        response = super().form_valid(form)
        student_id = self.kwargs.get('student_id')
        return redirect('student_detail', student_id=student_id)
    
    