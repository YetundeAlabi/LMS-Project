from django.urls import path

app_name = 'lms_admin'
from django.urls import path
from .views import (CohortCreateFormView, CohortListView, TutorListView, TutorCreateFormView, 
                    TutorDetailView, TutorDeleteView, TutorUpdateView, ToggleTutorSuspendView)

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
]
