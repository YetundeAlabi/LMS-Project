from django.urls import path, include
from .views import CourseListView, CourseDetail, CourseCreateView, CourseUpdateView

app_name= "course"
urlpatterns = [
    path('courses/', CourseListView.as_view(), name='course_list'),
    path('courses/<slug:course_slug>', CourseDetail.as_view(), name='course_detail'),
    path('courses/create_course', CourseCreateView.as_view(), name='create_course'),
    path('courses/<slug:course_slug>/update', CourseUpdateView.as_view(), name='update_course'),
]


