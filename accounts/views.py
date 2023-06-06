from typing import Any, Dict
from django.shortcuts import render
from django.contrib.auth import views
from django.urls import reverse 
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .models import User, Student, Tutor
from django.contrib.auth.views import PasswordChangeView
from django.views.generic.edit import UpdateView
from django.contrib.auth.views import LogoutView
from .forms import LoginForm,SignUpForm 
from django.shortcuts import get_object_or_404
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import Tutor, Student
from .forms import TutorUpdateForm, StudentUpdateForm, UserForm
# Create your views here.

User = get_user_model()


class TutorSignUpView(CreateView):
    model = Tutor
    form_class = UserForm
    template_name = 'accounts/signup.html' 
    success_url = reverse_lazy('login')

    # def form_valid(self, form):
    #     user = form.save(commit=False)
    #     user.role = User.TUTOR 
    #     user.save()
    #     tutor = Tutor(user=user)
    #     tutor.save()
    #     return super().form_valid(form)


class SignOutView(LogoutView):
    next_page = 'login'


class LoginView(views.LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs) :
        return super().get_context_data(**kwargs)
    
    def get_success_url(self) -> str:
        user = self.request.user
        if user.is_authenticated:
            if user.student:
                return reverse('student_home')
            elif user.tutor:
                return reverse('tutor_home')
            else:
                return reverse('admin_home')
        else:
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
    
    