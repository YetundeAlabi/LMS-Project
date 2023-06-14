from django.urls import path
from . import views


app_name='student'



urlpatterns = [
    path('student_courses/', views.StudentCourseListView.as_view(), name='course_list'),
    path('student_courses/<slug:student_course_slug>/student_topics/', views.StudentTopicListView.as_view(), name='topic_list'),
    path('student_courses/<slug:student_course_slug>/student_topics/<slug:student_topic_slug>/student_subtopics/<int:student_subtopic_id>/', views.StudentSubtopicDetailView.as_view(), name='student_subtopic_detail'),
    path('student_courses/<slug:student_course_slug>/student_topics/<slug:student_topic_slug>/student_subtopics/', views.StudentSubtopicListView.as_view(), name='student_subtopic_list'),
]