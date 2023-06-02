from django.urls import path

app_name = 'lms_admin'
from django.urls import path
from .views import (CohortCreateFormView, CohortListView, TutorListView, TutorCreateFormView, 
                    TutorDetailView, TutorDeleteView, TutorUpdateView, ToggleTutorSuspendView)

from lms_admin import views

app_name = "lms_admin"

urlpatterns = [
    path("tutor/", TutorListView.as_view(), name="tutor_list"),
    path("tutor/create/", TutorCreateFormView.as_view(), name="tutor_create"),
    path("tutor/<int:pk>/", TutorDetailView.as_view(), name="tutor_detail"),
    path("tutor/<int:pk>/update/", TutorUpdateView.as_view(), name="tutor_update"),
    path("tutor/<int:pk>/delete/", TutorDeleteView.as_view(), name="tutor_delete"),
    path("tutor/<int:pk>/togglesuspend/",
         ToggleTutorSuspendView.as_view(), name="tutor_toggle_suspend"),
    path("cohort/", CohortListView.as_view(), name="cohort_list"),
    path("cohort/create", CohortCreateFormView.as_view(), name="cohort_create"),
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
    path('import-students/', views.StudentImportView.as_view(), name='import_students'),
]
    

