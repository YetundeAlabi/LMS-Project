from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('reset_password/', 
        auth_views.PasswordResetView.as_view(template_name='accounts/password_reset_form.html'), 
        name='password_reset'),

    path('reset_password_sent/', 
        auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), 
        name='password_reset_done'),

    path('reset/<uidb64>/<token>', 
        auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), 
        name="password_reset_confirm"),

    path('reset_password_complete/', 
        auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), 
        name='password_reset_complete')
]