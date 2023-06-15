from django.urls import path
from . import views


app_name='student'



urlpatterns = [
    path('topics/<int:student_topic_id>/', views.StudentSubtopicListView.as_view(), name='subtopic_list'),
    path('topics/<int:student_topic_id>/<int:student_subtopic_id>/', views.StudentSubtopicDetailView.as_view(), name='subtopic_detail'),
    path('student_topic', views.StudentTopicView.as_view(), name= 'student_topic')
]