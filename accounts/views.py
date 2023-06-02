from typing import Any, Dict
from django.shortcuts import render
from django.contrib.auth import views
from django.urls import reverse 
from .forms import LoginForm
# Create your views here.

class LoginView(views.LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs) :
        return super().get_context_data(**kwargs)
    
    def get_success_url(self) -> str:
        user = self.request.user
        if user.is_authenticated:
            if user.role == "STUDENT":
                return reverse('student-home')
            elif user.role == 'TUTOR':
                return reverse('tutor-home')
            else:
                return reverse('admin-home')
        else:
            return reverse('login')
            