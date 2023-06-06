from django.urls import path

app_name = 'lms_admin'

from .views import (CohortCreateFormView, CohortListView, TutorListView, TutorCreateFormView, 
                    TutorDetailView, TutorDeleteView, TutorUpdateView, ToggleTutorSuspendView, ApplicantListView, ApplicantThankYouView)

from lms_admin import views

app_name = "lms_admin"

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name="dashboard"),
    path("tutor/", TutorListView.as_view(), name="tutor_list"),
    path("tutor/create/", TutorCreateFormView.as_view(), name="tutor_create"),
    path("tutor/<int:pk>/", TutorDetailView.as_view(), name="tutor_detail"),
    path("tutor/<int:pk>/update/", TutorUpdateView.as_view(), name="tutor_update"),
    path("tutor/<int:pk>/delete/", TutorDeleteView.as_view(), name="tutor_delete"),
    path("tutor/<int:pk>/togglesuspend/",
         ToggleTutorSuspendView.as_view(), name="tutor_toggle_suspend"),
    path("cohort/", CohortListView.as_view(), name="cohort_list"),
    path("cohort/create/", CohortCreateFormView.as_view(), name="cohort_create"),
    path("track/", views.TrackListView.as_view(), name="track_list"),
    path("track/create/", views.TrackCreateView.as_view(), name="track_create"),
    path("track/<slug:slug>/", views.TrackDetailView.as_view(), name="track_detail"),
    path("track/<slug:slug>/update/", views.TrackUpdateView.as_view(), name="track_update"),
    path("track/<slug:slug>/delete/", views.TrackDeleteView.as_view(), name="track_delete"),
    path("student/", views.StudentListView.as_view(), name="student_list"),
    path("student/create/", views.StudentCreateView.as_view(), name="student_create"),
    path("student/<int:pk>/", views.StudentDetailView.as_view(), name="student_detail"),
    path("student/<int:pk>/update/", views.StudentUpdateView.as_view(), name="student_update"),
    path("student/<int:pk>/delete/", views.StudentDeleteView.as_view(), name="student_delete"),
    path("student/<int:pk>/togglesuspend/", views.ToggleStudentSuspendView.as_view(), name="student_toggle_suspend"),
    path('import_students/', views.StudentImportView.as_view(), name='import_students'),
    path('apply/', views.ApplicantCreateView.as_view(), name="apply"),
    path('applicants_approval/', views.ApplicantApprovalFormView.as_view(), name="applicants_approval"),
    path('approved_applicants_export/', views.ExportApprovedApplicantsCSVView.as_view(), name="export_approved_applicants"),
    path('applicant_list/', ApplicantListView.as_view(), name='applicant_list'),
    path('applicant_thankyou/', ApplicantThankYouView.as_view(), name='applicant_thank_you'),
    
    
    
]
    

