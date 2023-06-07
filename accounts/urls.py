from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views
from .forms import CustomSetPasswordForm
from .views import TutorUpdateView, StudentUpdateView, TutorSignUpView, SignOutView, ChangePasswordView

app_name = 'accounts'
urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('reset_password/', 
        auth_views.PasswordResetView.as_view(template_name='accounts/password_reset_form.html'), 
        name='password_reset'),

    path('reset_password_sent/', 
        auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), 
        name='password_reset_done'),

    path('reset/<str:uidb64>/<str:token>', 
        auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), 
        name="password_reset_confirm"),

    path('reset_password_complete/', 
        auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), 
        name='password_reset_complete'),

    path('signup/', TutorSignUpView.as_view(), name='tutor_signup'),
    path('logout/', SignOutView.as_view(), name='logout'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('tutor_update/<int:tutor_id>/', TutorUpdateView.as_view(), name='tutor_update'),
    path('student_update/<int:student_id>/', StudentUpdateView.as_view(), name='student_update'),
    path('set_password/<str:uidb64>/<str:token>', 
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html', 
                                                     form_class = CustomSetPasswordForm,
                                                     success_url = reverse_lazy("accounts:password_reset_complete")
                                                     ),
         name='set_password'),
]
