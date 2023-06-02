from django.urls import path, include
from . import views

app_name= "course"
urlpatterns = [
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/create_course', views.CourseAndTopicCreateView.as_view(), name='create_course'),
    path('courses/<slug:course_slug>', views.CourseDetail.as_view(), name='course_detail'),
    path('courses/<slug:course_slug>/update', views.CourseUpdateView.as_view(), name='update_course'),
    path('courses/<slug:course_slug>/delete', views.CourseDeleteView.as_view(), name='update_course'),
    path('courses/<slug:course_slug>/topic/<uuid:pk>/update', views.TopicUpdateView.as_view(), name='update_topic'),
    path('courses/<slug:course_slug>/topic/<uuid:pk>/delete', views.TopicDeleteView.as_view(), name='delete_topic'),
    path('courses/<slug:course_slug>/topics/', views.TopicList.as_view(), name='topic_list'),
    path('courses/<slug:course_slug>/topic/<int:id>/delete', views.TopicDeleteView.as_view(), name='create_topic')
]


